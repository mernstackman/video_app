import tkinter as tk
from ttkbootstrap import Style, ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from .config import SEARCH_QUERIES
from .widgets.url_download import URLDownloadWidget
from .widgets.search_controls import SearchControlsWidget
from .widgets.crop_controls import CropControlsWidget
from .widgets.image_controls import ImageControlsWidget
from .widgets.text_controls import TextControlsWidget
from .widgets.sound_controls import SoundControlsWidget
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io
import ffmpeg
import os
import logging
import tempfile

class VideoSearchDownloadUI:
    def __init__(self, root, event_handler):
        self.root = root
        self.root.title("Video Search and Download")
        self.root.geometry("900x900")
        self.event_handler = event_handler
        self.style = Style()
        self.selected_video_path = tk.StringVar(value="")
        self.preview_image = None  # Store preview image reference
        self.original_frame = None  # Store the original PIL image for resizing
        self.no_video_displayed = False  # Flag to track if "No video selected" is shown
        self.crop_rectangle_id = None  # Store the ID of the cropping rectangle
        self.setup_logging()
        self.create_widgets()
        self.bind_focus_removal()  # Bind focus removal events

    def setup_logging(self):
        logging.basicConfig(filename='crop_debug.log', level=logging.DEBUG,
                           format='%(asctime)s - %(levelname)s - %(message)s')

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root, bootstyle=PRIMARY)
        self.notebook.pack(pady=5, padx=10, fill=BOTH, expand=True)

        self.search_download_tab = ttk.Frame(self.notebook)
        self.edit_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_download_tab, text="Search & Download")
        self.notebook.add(self.edit_tab, text="Edit")

        self.setup_search_download_tab()
        self.setup_edit_tab()

    def setup_search_download_tab(self):
        self.url_download_widget = URLDownloadWidget(self.search_download_tab, self.event_handler)
        self.url_download_widget.pack(pady=5, padx=10, fill=X)

        self.search_controls_widget = SearchControlsWidget(self.search_download_tab, self.event_handler, SEARCH_QUERIES)
        self.search_controls_widget.pack(pady=5, padx=10, fill=X)

        self.progress = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(self.search_download_tab, variable=self.progress, maximum=100, bootstyle=SUCCESS)
        self.progress_bar.pack(pady=5, padx=20, fill=X)

        self.status_text = tk.StringVar(value="Ready")
        ttk.Label(self.search_download_tab, textvariable=self.status_text, wraplength=650, bootstyle=INFO).pack(pady=5)

        ttk.Label(self.search_download_tab, text="Status Log:", bootstyle=SECONDARY).pack(pady=5)
        self.log_text = tk.Text(self.search_download_tab, height=8, width=60, state='disabled', wrap='word')
        self.log_text.pack(pady=5, padx=10)
        scrollbar = ttk.Scrollbar(self.search_download_tab, orient=VERTICAL, command=self.log_text.yview, bootstyle=SECONDARY)
        scrollbar.pack(side=RIGHT, fill=Y, pady=5)
        self.log_text['yscrollcommand'] = scrollbar.set

    def setup_edit_tab(self):
        main_pane = ttk.PanedWindow(self.edit_tab, orient=HORIZONTAL)
        main_pane.pack(fill=BOTH, expand=True, padx=10, pady=5)

        left_panel = ttk.Frame(main_pane)
        main_pane.add(left_panel, weight=1)
        left_panel.configure(style='TFrame', padding=5)
        left_panel.update_idletasks()
        left_panel.configure(width=300)

        ttk.Label(left_panel, text="Video Information", bootstyle=SECONDARY, font=("Arial", 12, "bold")).pack(pady=5)
        self.video_info = tk.StringVar(value="No video found in 'videos' folder.")
        info_label = ttk.Label(left_panel, textvariable=self.video_info, wraplength=250, justify=LEFT, bootstyle=INFO)
        info_label.pack(pady=5, padx=10, fill=X)

        ttk.Label(left_panel, text="Video Title:", bootstyle=SECONDARY).pack(pady=5)
        self.video_title = tk.StringVar(value="")
        title_entry = ttk.Entry(left_panel, textvariable=self.video_title, bootstyle=DEFAULT)
        title_entry.pack(pady=5, padx=10, fill=tk.X)
        self.add_context_menu(title_entry)

        button_frame_name = ttk.Frame(left_panel)
        button_frame_name.pack(pady=(5, 2), fill=tk.X, padx=10)
        button_frame_name.columnconfigure(1, weight=1)

        rename_auto = ttk.Button(button_frame_name, text="Auto Rename", command=self.event_handler.auto_rename, bootstyle=PRIMARY, width=12)
        rename_manual = ttk.Button(button_frame_name, text="Rename", command=self.event_handler.rename_video, bootstyle=PRIMARY, width=12)
        rename_auto.grid(row=0, column=0, padx=5, sticky='w')
        rename_manual.grid(row=0, column=2, padx=5, sticky='e')
        ToolTip(rename_auto, text="Generate a title based on video content", bootstyle=INFO)
        ToolTip(rename_manual, text="Apply the entered title to the video", bootstyle=INFO)

        button_frame_info = ttk.Frame(left_panel)
        button_frame_info.pack(pady=(2, 5), fill=tk.X, padx=10)
        button_frame_info.columnconfigure(1, weight=1)

        select_video = ttk.Button(button_frame_info, text="Select Video", command=lambda: [self.event_handler.select_video()], bootstyle=INFO, width=12)
        refresh_info = ttk.Button(button_frame_info, text="Refresh Info", command=lambda: [self.event_handler.update_video_info(), self.update_preview()], bootstyle=INFO, width=12)
        select_video.grid(row=0, column=0, padx=5, sticky='w')
        refresh_info.grid(row=0, column=2, padx=5, sticky='e')
        ToolTip(select_video, text="Choose a video file to edit", bootstyle=INFO)
        ToolTip(refresh_info, text="Update video information display", bootstyle=INFO)

        right_panel = ttk.PanedWindow(main_pane, orient=VERTICAL)
        main_pane.add(right_panel, weight=2)

        preview_frame = ttk.Frame(right_panel)
        right_panel.add(preview_frame, weight=1)
        ttk.Label(preview_frame, text="Preview", bootstyle=SECONDARY, font=("Arial", 12, "bold")).pack(pady=5)
        self.preview_canvas = tk.Canvas(preview_frame, bg="black", highlightthickness=0)
        self.preview_canvas.pack(pady=5, padx=10, fill=BOTH, expand=True)

        # Bind the canvas resize event to update the preview image or text
        self.preview_canvas.bind("<Configure>", self.on_canvas_resize)

        controls_frame = ttk.Frame(right_panel)
        right_panel.add(controls_frame, weight=1)
        ttk.Label(controls_frame, text="Editing Controls", bootstyle=SECONDARY, font=("Arial", 12, "bold")).pack(pady=5)

        edit_notebook = ttk.Notebook(controls_frame, bootstyle=SECONDARY)
        edit_notebook.pack(pady=5, padx=10, fill=BOTH, expand=True)

        crop_tab = ttk.Frame(edit_notebook)
        image_tab = ttk.Frame(edit_notebook)
        text_tab = ttk.Frame(edit_notebook)
        sound_tab = ttk.Frame(edit_notebook)
        edit_notebook.add(crop_tab, text="Crop")
        edit_notebook.add(image_tab, text="Image")
        edit_notebook.add(text_tab, text="Text")
        edit_notebook.add(sound_tab, text="Sound")

        self.crop_controls_widget = CropControlsWidget(crop_tab, self.event_handler)
        self.crop_controls_widget.pack(pady=5, padx=10, fill=X)

        self.image_controls_widget = ImageControlsWidget(image_tab, self.event_handler)
        self.image_controls_widget.pack(pady=5, padx=10, fill=X)

        self.text_controls_widget = TextControlsWidget(text_tab, self.event_handler)
        self.text_controls_widget.pack(pady=5, padx=10, fill=X)

        self.sound_controls_widget = SoundControlsWidget(sound_tab, self.event_handler)
        self.sound_controls_widget.pack(pady=5, padx=10, fill=X)

        ttk.Label(self.edit_tab, text="Note: Edits the selected or first video in 'videos' folder. Output saved to 'Edited' folder.",
                  font=("Arial", 8, "italic"), bootstyle=SECONDARY).pack(pady=5)

        # Initialize preview for default video
        self.update_preview()

    def bind_focus_removal(self):
        """Bind click events to remove focus from input fields when clicking outside."""
        def remove_focus(event):
            widget = event.widget
            if not isinstance(widget, (ttk.Entry, tk.Entry)):
                self.root.focus_set()

        self.root.bind("<Button-1>", remove_focus)
        self.notebook.bind("<Button-1>", remove_focus)
        self.search_download_tab.bind("<Button-1>", remove_focus)
        self.edit_tab.bind("<Button-1>", remove_focus)
        self.preview_canvas.bind("<Button-1>", remove_focus)

    def add_context_menu(self, entry):
        """Add a right-click context menu to an entry widget."""
        menu = tk.Menu(entry, tearoff=0)
        menu.add_command(label="Copy", command=lambda: entry.event_generate("<<Copy>>"))
        menu.add_command(label="Cut", command=lambda: entry.event_generate("<<Cut>>"))
        menu.add_command(label="Paste", command=lambda: entry.event_generate("<<Paste>>"))
        menu.add_command(label="Select All", command=lambda: entry.event_generate("<<SelectAll>>"))

        def show_context_menu(event):
            menu.post(event.x_root, event.y_root)

        entry.bind("<Button-3>", show_context_menu)

    def update_status(self, message):
        self.status_text.set(message)
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update()
        logging.debug(f"Status updated: {message}")

    def update_progress(self, value):
        self.progress.set(value)
        self.root.update()
        logging.debug(f"Progress updated: {value}%")

    def draw_crop_rectangle(self, canvas_width, canvas_height, orig_width, orig_height, x1, y1, x2, y2):
        """Draw a cropping rectangle on the canvas, scaled to the preview image dimensions."""
        if self.crop_rectangle_id:
            self.preview_canvas.delete(self.crop_rectangle_id)
            logging.debug("Deleted previous crop rectangle")

        # Calculate scaling factor for the preview image
        scale = min(canvas_width / orig_width, canvas_height / orig_height)
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)
        x_offset = (canvas_width - new_width) / 2
        y_offset = (canvas_height - new_height) / 2

        # Scale crop coordinates
        rect_x1 = x_offset + (x1 * scale)
        rect_y1 = y_offset + (y1 * scale)
        rect_x2 = x_offset + (x2 * scale)
        rect_y2 = y_offset + (y2 * scale)

        # Ensure valid rectangle coordinates
        rect_x1 = max(x_offset, min(rect_x1, x_offset + new_width - 1))
        rect_y1 = max(y_offset, min(rect_y1, y_offset + new_height - 1))
        rect_x2 = max(rect_x1 + 1, min(rect_x2, x_offset + new_width))
        rect_y2 = max(rect_y1 + 1, min(rect_y2, y_offset + new_height))

        # Draw the rectangle
        self.crop_rectangle_id = self.preview_canvas.create_rectangle(
            rect_x1, rect_y1, rect_x2, rect_y2,
            outline="white", width=2, dash=(4, 4)
        )
        logging.debug(f"Drew crop rectangle at canvas coords: ({rect_x1}, {rect_y1}, {rect_x2}, {rect_y2})")

    def on_canvas_resize(self, event):
        """Handle canvas resize by updating the preview image or text and redrawing the crop rectangle."""
        logging.debug(f"Canvas resized: width={event.width}, height={event.height}")
        if self.no_video_displayed:
            self.preview_canvas.delete("all")
            canvas_width = event.width
            canvas_height = event.height
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 400
                canvas_height = 225
            self.preview_canvas.create_text(
                canvas_width / 2, 
                canvas_height / 2, 
                text="No video selected", 
                fill="white", 
                font=("Arial", 10),
                anchor="center"
            )
            logging.debug("Displayed 'No video selected' text")
        elif self.original_frame:
            self.update_preview_image(event.width, event.height)
            # Redraw crop rectangle if crop parameters are set
            try:
                x1 = int(self.crop_controls_widget.crop_x1.get() or 0)
                y1 = int(self.crop_controls_widget.crop_y1.get() or 0)
                x2 = int(self.crop_controls_widget.crop_x2.get() or 0)
                y2 = int(self.crop_controls_widget.crop_y2.get() or 0)
                orig_width, orig_height = self.original_frame.size
                self.draw_crop_rectangle(event.width, event.height, orig_width, orig_height, x1, y1, x2, y2)
            except ValueError:
                logging.debug("Invalid crop parameters for rectangle on resize, skipping")
            logging.debug("Updated preview image and crop rectangle on canvas resize")

    def update_preview(self, update_rectangle_only=False):
        """Update the preview canvas with a frame from the selected video, applying cropping, image overlay, text overlay, and sound adjustments.
        If update_rectangle_only is True, only update the crop rectangle."""
        logging.debug(f"update_preview called, update_rectangle_only={update_rectangle_only}")
        video_path = self.selected_video_path.get()
        if not update_rectangle_only:
            self.preview_canvas.delete("all")  # Clear previous content
            self.original_frame = None  # Reset original frame
            self.no_video_displayed = False  # Reset the flag
            self.crop_rectangle_id = None  # Reset rectangle ID

        self.preview_canvas.update_idletasks()
        logging.debug(f"Video path: {video_path}")

        if not video_path or not os.path.exists(video_path):
            self.no_video_displayed = True
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 400
                canvas_height = 225

            self.preview_canvas.create_text(
                canvas_width / 2, 
                canvas_height / 2, 
                text="No video selected", 
                fill="white", 
                font=("Arial", 10),
                anchor="center"
            )
            logging.debug("No video selected, displayed message")
            return

        try:
            if not update_rectangle_only:
                logging.debug("Probing video")
                probe = ffmpeg.probe(video_path)
                video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
                if not video_stream:
                    raise ValueError("No video stream found")
                
                logging.debug("Extracting frame")
                frame = ffmpeg.input(video_path, ss=1).output('pipe:', format='image2', vframes=1).run(capture_stdout=True)[0]
                image = Image.open(io.BytesIO(frame))
                logging.debug(f"Frame extracted: size={image.size}")

                orig_width = int(video_stream['width'])
                orig_height = int(video_stream['height'])
                logging.debug(f"Original video dimensions: {orig_width}x{orig_height}")

                # Apply cropping
                try:
                    x1 = int(self.crop_controls_widget.crop_x1.get() or 0)
                    y1 = int(self.crop_controls_widget.crop_y1.get() or 0)
                    x2 = int(self.crop_controls_widget.crop_x2.get() or 0)
                    y2 = int(self.crop_controls_widget.crop_y2.get() or 0)
                except ValueError:
                    x1, y1, x2, y2 = 0, 0, orig_width, orig_height
                    logging.debug("Invalid crop parameters, using defaults")

                x1 = max(0, min(x1, orig_width - 1))
                y1 = max(0, min(y1, orig_height - 1))
                x2 = max(x1 + 1, min(x2, orig_width))
                y2 = max(y1 + 1, min(y2, orig_height))
                logging.debug(f"Crop parameters: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

                if x1 != 0 or y1 != 0 or x2 != orig_width or y2 != orig_height:
                    image = image.crop((x1, y1, x2, y2))
                    logging.debug(f"Cropped image to: {image.size}")

                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                    logging.debug("Converted image to RGBA")

                # Apply image overlay if selected
                overlay_image_path = self.image_controls_widget.overlay_image_path.get()
                if overlay_image_path and os.path.exists(overlay_image_path):
                    try:
                        overlay_image = Image.open(overlay_image_path)
                        logging.debug(f"Loaded overlay image: {overlay_image_path}")
                        try:
                            overlay_x = int(self.image_controls_widget.overlay_x.get() or 0)
                            overlay_y = int(self.image_controls_widget.overlay_y.get() or 0)
                            overlay_scale = float(self.image_controls_widget.overlay_scale.get() or 1.0)
                            overlay_opacity = float(self.image_controls_widget.overlay_opacity.get() or 1.0)
                            overlay_scale = max(0.1, overlay_scale)
                            overlay_opacity = max(0.0, min(1.0, overlay_opacity))
                        except ValueError:
                            overlay_x, overlay_y, overlay_scale, overlay_opacity = 0, 0, 1.0, 1.0
                            logging.debug("Invalid overlay parameters, using defaults")

                        overlay_width, overlay_height = overlay_image.size
                        new_overlay_width = int(overlay_width * overlay_scale)
                        new_overlay_height = int(overlay_height * overlay_scale)
                        overlay_image = overlay_image.resize((new_overlay_width, new_overlay_height), Image.Resampling.LANCZOS)
                        logging.debug(f"Resized overlay image to: {new_overlay_width}x{new_overlay_height}")

                        if overlay_image.mode != 'RGBA':
                            overlay_image = overlay_image.convert('RGBA')
                            logging.debug("Converted overlay image to RGBA")

                        # Apply opacity to the overlay image
                        alpha = overlay_image.split()[3]
                        alpha = alpha.point(lambda p: p * overlay_opacity)
                        overlay_image.putalpha(alpha)
                        logging.debug(f"Applied overlay opacity: {overlay_opacity}")

                        overlay_x = max(0, min(overlay_x, image.width - new_overlay_width))
                        overlay_y = max(0, min(overlay_y, image.height - new_overlay_height))

                        new_image = Image.new('RGBA', image.size)
                        new_image.paste(image, (0, 0))
                        new_image.paste(overlay_image, (overlay_x, overlay_y), overlay_image)
                        image = new_image
                        logging.debug(f"Applied overlay at position: ({overlay_x}, {overlay_y})")
                    except Exception as e:
                        self.update_status(f"Error applying image overlay to preview: {str(e)}")
                        logging.error(f"Error applying image overlay: {str(e)}")

                # Apply text overlay if specified
                overlay_text = self.text_controls_widget.overlay_text.get()
                if overlay_text:
                    try:
                        logging.debug(f"Applying text overlay: {overlay_text}")
                        try:
                            text_x = int(self.text_controls_widget.text_x.get() or 10)
                            text_y = int(self.text_controls_widget.text_y.get() or 10)
                            font_size = int(self.text_controls_widget.text_font_size.get() or 24)
                            text_color = self.text_controls_widget.text_color.get() or "white"
                            font_name = self.text_controls_widget.text_font.get() or "arial.ttf"
                            text_opacity = float(self.text_controls_widget.text_opacity.get() or 1.0)
                            text_opacity = max(0.0, min(1.0, text_opacity))
                        except ValueError as e:
                            text_x, text_y, font_size, text_color, font_name, text_opacity = 10, 10, 24, "white", "arial.ttf", 1.0
                            logging.debug(f"Invalid text parameters, using defaults: {str(e)}")

                        logging.debug(f"Text parameters: x={text_x}, y={text_y}, size={font_size}, color={text_color}, font={font_name}, opacity={text_opacity}")

                        # Load the font
                        try:
                            font = ImageFont.truetype(font_name, font_size)
                            logging.debug(f"Loaded font: {font_name}, size={font_size}")
                        except IOError:
                            # Fallback to Arial with full path
                            try:
                                font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", font_size)
                                font_name = "Arial"
                                self.update_status(f"Font '{font_name}' not found, using Arial.")
                                logging.debug(f"Fallback to Arial, size={font_size}")
                            except IOError:
                                font = ImageFont.truetype("arial.ttf", font_size)  # Last resort
                                self.update_status(f"No TrueType fonts found, using system Arial.")
                                logging.debug(f"Fallback to system Arial, size={font_size}")

                        # Validate text position
                        text_x = max(0, min(text_x, image.width - 10))
                        text_y = max(0, min(text_y, image.height - 10))
                        logging.debug(f"Validated text position: ({text_x}, {text_y})")

                        # Create a transparent layer for the text
                        text_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
                        draw = ImageDraw.Draw(text_layer)

                        # Calculate text bounding box for debugging
                        text_bbox = draw.textbbox((text_x, text_y), overlay_text, font=font)
                        logging.debug(f"Text bounding box: {text_bbox} (width={text_bbox[2]-text_bbox[0]}, height={text_bbox[3]-text_bbox[1]})")

                        # Draw the text with full opacity
                        draw.text((text_x, text_y), overlay_text, fill=text_color, font=font)
                        logging.debug(f"Drew text: '{overlay_text}' at ({text_x}, {text_y})")

                        # Apply opacity to the text layer
                        if text_opacity < 1.0:
                            alpha = text_layer.split()[3]
                            alpha = alpha.point(lambda p: p * text_opacity)
                            text_layer.putalpha(alpha)
                            logging.debug(f"Applied text opacity: {text_opacity}")

                        # Composite the text layer onto the main image
                        image = Image.alpha_composite(image, text_layer)
                        logging.debug("Composited text layer onto image")
                    except Exception as e:
                        self.update_status(f"Error applying text overlay to preview: {str(e)}")
                        logging.error(f"Error applying text overlay: {str(e)}")

                # Apply sound adjustments if specified
                try:
                    volume = float(self.sound_controls_widget.volume.get() or 1.0)
                    volume = max(0.0, min(2.0, volume))  # Clamp between 0.0 and 2.0
                    logging.debug(f"Applying sound volume: {volume}")
                    if volume != 1.0:
                        # Create a temporary file to store the adjusted audio
                        temp_output = os.path.join(tempfile.gettempdir(), "preview_audio.mp4")
                        ffmpeg.input(video_path).output(temp_output, af=f"volume={volume}", vframes=1, y='y').run(overwrite_output=True)
                        logging.debug(f"Created temporary audio preview file: {temp_output}")
                        self.update_status(f"Sound volume set to {volume}x. Preview applied.")
                    else:
                        logging.debug("No volume adjustment needed (volume=1.0)")
                except ValueError:
                    volume = 1.0
                    logging.debug("Invalid volume parameter, using default: 1.0")
                except Exception as e:
                    self.update_status(f"Error applying sound volume: {str(e)}")
                    logging.error(f"Error applying sound volume: {str(e)}")

                self.original_frame = image
                logging.debug(f"Stored original frame: size={image.size}")

                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                if canvas_width <= 1 or canvas_height <= 1:
                    canvas_width = 400
                    canvas_height = 225
                logging.debug(f"Canvas size for preview: {canvas_width}x{canvas_height}")
                self.update_preview_image(canvas_width, canvas_height)

            # Draw or update the crop rectangle
            try:
                x1 = int(self.crop_controls_widget.crop_x1.get() or 0)
                y1 = int(self.crop_controls_widget.crop_y1.get() or 0)
                x2 = int(self.crop_controls_widget.crop_x2.get() or 0)
                y2 = int(self.crop_controls_widget.crop_y2.get() or 0)
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                if canvas_width <= 1 or canvas_height <= 1:
                    canvas_width = 400
                    canvas_height = 225
                orig_width = int(probe['streams'][0]['width'])
                orig_height = int(probe['streams'][0]['height'])
                self.draw_crop_rectangle(canvas_width, canvas_height, orig_width, orig_height, x1, y1, x2, y2)
            except (ValueError, NameError):
                logging.debug("Invalid crop parameters or no video stream, skipping crop rectangle")
        except Exception as e:
            self.no_video_displayed = True
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 400
                canvas_height = 225

            self.preview_canvas.create_text(
                canvas_width / 2, 
                canvas_height / 2, 
                text=f"Preview Error: {str(e)}", 
                fill="white", 
                font=("Arial", 10),
                anchor="center"
            )
            logging.error(f"Preview error: {str(e)}")

    def update_preview_image(self, canvas_width, canvas_height):
        """Scale the preview image to fit the canvas while preserving aspect ratio."""
        if not self.original_frame:
            logging.debug("No original frame to update preview image")
            return
        self.preview_canvas.delete("all")
        orig_width, orig_height = self.original_frame.size
        scale = min(canvas_width / orig_width, canvas_height / orig_height)
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)
        logging.debug(f"Resizing image to: {new_width}x{new_height}, scale={scale}")
        resized_image = self.original_frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.preview_image = ImageTk.PhotoImage(resized_image)
        x_offset = (canvas_width - new_width) / 2
        y_offset = (canvas_height - new_height) / 2
        self.preview_canvas.create_image(x_offset, y_offset, anchor='nw', image=self.preview_image)
        logging.debug(f"Displayed preview image at offset: ({x_offset}, {y_offset})")