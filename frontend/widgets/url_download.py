import tkinter as tk
from ttkbootstrap import ttk
from ttkbootstrap.constants import *

class URLDownloadWidget(ttk.Frame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Download from URL:", bootstyle=SECONDARY).pack(pady=5)

        self.url_input = tk.StringVar()
        url_entry = ttk.Entry(self, textvariable=self.url_input, width=50, bootstyle=DEFAULT)
        url_entry.pack(pady=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(url_entry)  # Add context menu

        options_frame = ttk.Frame(self)
        options_frame.pack(pady=5)

        self.resolution = tk.StringVar(value="best")
        ttk.Label(options_frame, text="Resolution:", bootstyle=SECONDARY).pack(side=LEFT, padx=5)
        ttk.Combobox(options_frame, textvariable=self.resolution, values=["best", "1080p", "720p", "360p"], width=10, state="readonly", bootstyle=DEFAULT).pack(side=LEFT, padx=5)

        self.extension = tk.StringVar(value=".mp4")
        ttk.Label(options_frame, text="Extension:", bootstyle=SECONDARY).pack(side=LEFT, padx=5)
        ttk.Combobox(options_frame, textvariable=self.extension, values=[".mp4", ".webm", ".mkv"], width=10, state="readonly", bootstyle=DEFAULT).pack(side=LEFT, padx=5)

        ttk.Button(self, text="Download", command=self.event_handler.download_from_url, bootstyle=PRIMARY).pack(pady=5)