import tkinter as tk
from ttkbootstrap import Style, ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from .config import SEARCH_QUERIES
from .widgets.url_download import URLDownloadWidget
from .widgets.search_controls import SearchControlsWidget
from .widgets.crop_controls import CropControlsWidget
from .widgets.overlay_controls import OverlayControlsWidget
from PIL import Image, ImageTk
import io
import ffmpeg
import os

class VideoSearchDownloadUI:
    def __init__(self, root, event_handler):
        self.root = root
        self.root.title("Video Search and Download")
        self.root.geometry("900x900")
        self.event_handler = event_handler
        self.style = Style()
        self.selected_video_path = tk.StringVar(value="")
        self.preview_image = None  # Store preview image reference
        self.create_widgets()

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

        select_video = ttk.Button(button_frame_info, text="Select Video", command=lambda: [self.event_handler.select_video(), self.update_preview()], bootstyle=INFO, width=12)
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
        self.preview_canvas = tk.Canvas(preview_frame, width=400, height=225, bg="black", highlightthickness=0)
        self.preview_canvas.pack(pady=5, padx=10)

        controls_frame = ttk.Frame(right_panel)
        right_panel.add(controls_frame, weight=1)
        ttk.Label(controls_frame, text="Editing Controls", bootstyle=SECONDARY, font=("Arial", 12, "bold")).pack(pady=5)

        edit_notebook = ttk.Notebook(controls_frame, bootstyle=SECONDARY)
        edit_notebook.pack(pady=5, padx=10, fill=BOTH, expand=True)

        crop_tab = ttk.Frame(edit_notebook)
        overlay_tab = ttk.Frame(edit_notebook)
        edit_notebook.add(crop_tab, text="Crop")
        edit_notebook.add(overlay_tab, text="Overlay")

        self.crop_controls_widget = CropControlsWidget(crop_tab, self.event_handler)
        self.crop_controls_widget.pack(pady=5, padx=10, fill=X)

        self.overlay_controls_widget = OverlayControlsWidget(overlay_tab, self.event_handler)
        self.overlay_controls_widget.pack(pady=5, padx=10, fill=X)

        ttk.Label(self.edit_tab, text="Note: Edits the selected or first video in 'videos' folder. Output saved to 'Edited' folder.",
                  font=("Arial", 8, "italic"), bootstyle=SECONDARY).pack(pady=5)

        # Initialize preview for default video
        self.update_preview()

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

    def update_progress(self, value):
        self.progress.set(value)
        self.root.update()

    def update_preview(self):
        """Update the preview canvas with a frame from the selected video."""
        video_path = self.selected_video_path.get()
        self.preview_canvas.delete("all")  # Clear previous content
        if not video_path or not os.path.exists(video_path):
            self.preview_canvas.create_text(200, 112.5, text="No video selected", fill="white", font=("Arial", 10))
            return
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
            if not video_stream:
                raise ValueError("No video stream found")
            width, height = int(video_stream['width']), int(video_stream['height'])
            scale = min(400/width, 225/height)
            frame = ffmpeg.input(video_path, ss=1).filter('scale', int(width*scale), int(height*scale)).output('pipe:', format='image2', vframes=1).run(capture_stdout=True)[0]
            image = Image.open(io.BytesIO(frame))
            self.preview_image = ImageTk.PhotoImage(image)
            self.preview_canvas.create_image(0, 0, anchor='nw', image=self.preview_image)
        except Exception as e:
            self.preview_canvas.create_text(200, 112.5, text=f"Preview Error: {str(e)}", fill="white", font=("Arial", 10))