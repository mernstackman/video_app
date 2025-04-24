import os
import json
import logging
from tkinter import filedialog
import ffmpeg
from backend.downloader import Downloader
from backend.editor import Editor
from backend.utils import clean_title

class EventHandler:
    def __init__(self, ui):
        self.ui = ui
        self.downloader = Downloader()
        self.editor = Editor()
        self.setup_logging()
        self.videos_dir = os.path.join(os.getcwd(), "videos")
        self.edited_dir = os.path.join(os.getcwd(), "Edited")
        os.makedirs(self.videos_dir, exist_ok=True)
        os.makedirs(self.edited_dir, exist_ok=True)

    def setup_logging(self):
        logging.basicConfig(filename='crop_debug.log', level=logging.DEBUG,
                           format='%(asctime)s - %(levelname)s - %(message)s')

    def select_video(self):
        file_path = filedialog.askopenfilename(
            initialdir=self.videos_dir,
            title="Select Video",
            filetypes=(("Video files", "*.mp4 *.webm *.mkv"), ("All files", "*.*"))
        )
        if file_path:
            self.ui.selected_video_path.set(file_path)
            self.update_video_info()
            logging.info(f"Selected video: {file_path}")

    def select_overlay_image(self):
        file_path = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select Overlay Image",
            filetypes=(("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*"))
        )
        if file_path:
            self.ui.overlay_controls_widget.overlay_image_path.set(file_path)
            self.ui.update_status(f"Selected overlay image: {os.path.basename(file_path)}")
            logging.info(f"Selected overlay image: {file_path}")

    def update_video_info(self):
        video_path = self.ui.selected_video_path.get()
        if not video_path or not os.path.exists(video_path):
            video_path = self.get_first_video()
            self.ui.selected_video_path.set(video_path if video_path else "")
        if not video_path:
            self.ui.video_info.set("No video found in 'videos' folder.")
            return
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
            if video_stream:
                width = video_stream.get('width', 'Unknown')
                height = video_stream.get('height', 'Unknown')
                duration = float(probe['format'].get('duration', 0))
                info = f"Title: {os.path.basename(video_path)}\nResolution: {width}x{height}\nDuration: {duration:.2f} seconds"
                self.ui.video_info.set(info)
                self.ui.video_title.set(clean_title(os.path.basename(video_path)))
            else:
                self.ui.video_info.set("No video stream found.")
            logging.info(f"Updated video info for: {video_path}")
        except Exception as e:
            self.ui.video_info.set(f"Error loading video info: {str(e)}")
            logging.error(f"Error updating video info: {str(e)}")

    def get_first_video(self):
        extensions = ('.mp4', '.webm', '.mkv')
        for file in os.listdir(self.videos_dir):
            if file.lower().endswith(extensions):
                return os.path.join(self.videos_dir, file)
        return ""

    def download_from_url(self):
        url = self.ui.url_download_widget.url_input.get()
        resolution = self.ui.url_download_widget.resolution.get()
        extension = self.ui.url_download_widget.extension.get()
        if not url:
            self.ui.update_status("Please enter a URL.")
            return
        try:
            success, message = self.downloader.download_from_url(
                url, resolution, extension,
                progress_callback=self.ui.update_status
            )
            if success:
                self.ui.selected_video_path.set(message)  # Set downloaded video path
                self.update_video_info()
            else:
                self.ui.update_status(message)
        except Exception as e:
            self.ui.update_status(f"Download failed: {str(e)}")
            logging.error(f"Download failed: {str(e)}")

    def search_videos(self):
        query = self.ui.search_controls_widget.custom_query.get() or self.ui.search_controls_widget.selected_query.get()
        results_length = int(self.ui.search_controls_widget.results_length.get() or 5)
        if query == "Select a query or enter custom below":
            self.ui.update_status("Please select or enter a query.")
            return
        try:
            queries = [query]  # Single query for populate_search_results
            self.downloader.populate_search_results(
                queries, results_length,
                progress_callback=self.ui.update_status
            )
        except Exception as e:
            self.ui.update_status(f"Search failed: {str(e)}")
            logging.error(f"Search failed: {str(e)}")

    def download_videos(self):
        max_downloads = int(self.ui.search_controls_widget.max_downloads.get() or 1)
        try:
            success, video_paths = self.downloader.download_next_video(
                progress_callback=self.ui.update_status,
                max_downloads=max_downloads,
                progress_updater=self.ui.update_progress
            )
            if success and video_paths:
                # Set the first downloaded video as selected
                self.ui.selected_video_path.set(video_paths[0][0])
                self.update_video_info()
            else:
                self.ui.update_status("No videos downloaded.")
        except Exception as e:
            self.ui.update_status(f"Download failed: {str(e)}")
            logging.error(f"Download failed: {str(e)}")

    def crop_video(self):
        video_path = self.ui.selected_video_path.get() or self.get_first_video()
        if not video_path:
            self.ui.update_status("No video selected for cropping.")
            return
        try:
            x1 = int(self.ui.crop_controls_widget.crop_x1.get() or 0)
            y1 = int(self.ui.crop_controls_widget.crop_y1.get() or 0)
            x2 = int(self.ui.crop_controls_widget.crop_x2.get() or 0)
            y2 = int(self.ui.crop_controls_widget.crop_y2.get() or 0)
            preserve_aspect = self.ui.crop_controls_widget.preserve_aspect.get()
            output_path = os.path.join(self.edited_dir, f"cropped_{os.path.basename(video_path)}")
            self.editor.edit_video_crop(video_path, output_path, (x1, y1, x2, y2), self.ui.update_progress, preserve_aspect)
            self.ui.update_status(f"Video cropped and saved to {output_path}")
            logging.info(f"Video cropped: {output_path}")
        except Exception as e:
            self.ui.update_status(f"Crop failed: {str(e)}")
            logging.error(f"Crop failed: {str(e)}")

    def apply_overlays(self):
        video_path = self.ui.selected_video_path.get() or self.get_first_video()
        if not video_path:
            self.ui.update_status("No video selected for overlay.")
            return
        try:
            overlay_params = {
                'image_path': self.ui.overlay_controls_widget.overlay_image_path.get(),
                'x': int(self.ui.overlay_controls_widget.overlay_x.get() or 0),
                'y': int(self.ui.overlay_controls_widget.overlay_y.get() or 0),
                'scale': float(self.ui.overlay_controls_widget.overlay_scale.get() or 1.0)
            } if self.ui.overlay_controls_widget.overlay_image_path.get() else None
            text_params = {
                'text': self.ui.overlay_controls_widget.overlay_text.get(),
                'font_size': int(self.ui.overlay_controls_widget.text_font_size.get() or 24),
                'color': self.ui.overlay_controls_widget.text_color.get() or 'white',
                'x': int(self.ui.overlay_controls_widget.text_x.get() or 10),
                'y': int(self.ui.overlay_controls_widget.text_y.get() or 10)
            } if self.ui.overlay_controls_widget.overlay_text.get() else None
            output_path = os.path.join(self.edited_dir, f"overlay_{os.path.basename(video_path)}")
            self.editor.edit_video_overlays(video_path, output_path, overlay_params, text_params, self.ui.update_progress)
            self.ui.update_status(f"Overlay applied and saved to {output_path}")
            logging.info(f"Overlay applied: {output_path}")
        except Exception as e:
            self.ui.update_status(f"Overlay failed: {str(e)}")
            logging.error(f"Overlay failed: {str(e)}")

    def auto_rename(self):
        video_path = self.ui.selected_video_path.get() or self.get_first_video()
        if not video_path:
            self.ui.update_status("No video selected for renaming.")
            return
        try:
            new_title = clean_title(os.path.basename(video_path)) + "_auto"
            self.ui.video_title.set(new_title)
            self.ui.update_status("Auto-renamed title generated. Click 'Rename' to apply.")
            logging.info(f"Auto-renamed title: {new_title}")
        except Exception as e:
            self.ui.update_status(f"Auto-rename failed: {str(e)}")
            logging.error(f"Auto-rename failed: {str(e)}")

    def rename_video(self):
        video_path = self.ui.selected_video_path.get() or self.get_first_video()
        new_title = self.ui.video_title.get()
        if not video_path or not new_title:
            self.ui.update_status("No video selected or title provided.")
            return
        try:
            new_filename = clean_title(new_title) + os.path.splitext(video_path)[1]
            new_path = os.path.join(self.videos_dir, new_filename)
            os.rename(video_path, new_path)
            self.ui.selected_video_path.set(new_path)
            self.update_video_info()
            self.ui.update_status(f"Video renamed to {new_filename}")
            logging.info(f"Video renamed: {new_path}")
        except Exception as e:
            self.ui.update_status(f"Rename failed: {str(e)}")
            logging.error(f"Rename failed: {str(e)}")