import tkinter as tk
from ttkbootstrap import ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
import logging

class ImageControlsWidget(ttk.Frame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.setup_logging()
        self.create_widgets()

    def setup_logging(self):
        logging.basicConfig(filename='crop_debug.log', level=logging.DEBUG,
                           format='%(asctime)s - %(levelname)s - %(message)s')

    def create_widgets(self):
        # Image Overlay Section
        ttk.Label(self, text="Image Overlay:", bootstyle=SECONDARY).pack(pady=5)
        image_frame = ttk.Frame(self)
        image_frame.pack(pady=5)

        self.overlay_image_path = tk.StringVar(value="")
        self.overlay_x = tk.StringVar(value="0")
        self.overlay_y = tk.StringVar(value="0")
        self.overlay_scale = tk.StringVar(value="1.0")
        self.overlay_opacity = tk.StringVar(value="1.0")

        # Image Path
        ttk.Label(image_frame, text="Image:", bootstyle=SECONDARY).grid(row=0, column=0, padx=5)
        image_entry = ttk.Entry(image_frame, textvariable=self.overlay_image_path, width=20, bootstyle=DEFAULT)
        image_entry.grid(row=0, column=1, padx=5, columnspan=2)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(image_entry)
        ttk.Button(image_frame, text="Browse", command=self.browse_image, bootstyle=PRIMARY).grid(row=0, column=3, padx=5)
        logging.debug("Image entry bindings set")

        # Position (X, Y)
        ttk.Label(image_frame, text="X:", bootstyle=SECONDARY).grid(row=1, column=0, padx=5)
        x_entry = ttk.Entry(image_frame, textvariable=self.overlay_x, width=10, bootstyle=DEFAULT)
        x_entry.grid(row=1, column=1, padx=5)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(x_entry)
        logging.debug("Overlay X entry bindings set")

        ttk.Label(image_frame, text="Y:", bootstyle=SECONDARY).grid(row=1, column=2, padx=5)
        y_entry = ttk.Entry(image_frame, textvariable=self.overlay_y, width=10, bootstyle=DEFAULT)
        y_entry.grid(row=1, column=3, padx=5)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(y_entry)
        logging.debug("Overlay Y entry bindings set")

        # Scale and Opacity
        ttk.Label(image_frame, text="Scale:", bootstyle=SECONDARY).grid(row=2, column=0, padx=5)
        scale_entry = ttk.Entry(image_frame, textvariable=self.overlay_scale, width=10, bootstyle=DEFAULT)
        scale_entry.grid(row=2, column=1, padx=5)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(scale_entry)
        logging.debug("Scale entry bindings set")

        ttk.Label(image_frame, text="Opacity (0-1):", bootstyle=SECONDARY).grid(row=2, column=2, padx=5)
        opacity_entry = ttk.Entry(image_frame, textvariable=self.overlay_opacity, width=10, bootstyle=DEFAULT)
        opacity_entry.grid(row=2, column=3, padx=5)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(opacity_entry)
        logging.debug("Opacity entry bindings set")

        # Preview Image Overlay Button
        ttk.Button(image_frame, text="Preview Image Overlay", command=self.preview_image_overlay, bootstyle=PRIMARY).grid(row=3, column=0, columnspan=4, pady=5)
        logging.debug("Preview Image Overlay button added")

    def browse_image(self):
        """Open a file dialog to select an overlay image."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if file_path:
            self.overlay_image_path.set(file_path)
            logging.debug(f"Selected overlay image: {file_path}")

    def preview_image_overlay(self):
        """Trigger preview update for image overlay parameters."""
        if self.event_handler.ui:
            logging.debug(f"Preview Image Overlay triggered: path={self.overlay_image_path.get()}, "
                         f"x={self.overlay_x.get()}, y={self.overlay_y.get()}, "
                         f"scale={self.overlay_scale.get()}, opacity={self.overlay_opacity.get()}")
            self.event_handler.ui.update_preview()
        else:
            logging.error("UI not set in event_handler")