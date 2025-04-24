import tkinter as tk
from ttkbootstrap import ttk
from ttkbootstrap.constants import *

class OverlayControlsWidget(ttk.Frame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Image Overlay:", bootstyle=SECONDARY).pack(pady=5)
        self.overlay_image_path = tk.StringVar(value="")
        ttk.Button(self, text="Select Image", command=self.event_handler.select_overlay_image, bootstyle=INFO).pack(pady=5)
        ttk.Label(self, textvariable=self.overlay_image_path, wraplength=650, font=("Arial", 8), bootstyle=INFO).pack(pady=5)

        overlay_frame = ttk.Frame(self)
        overlay_frame.pack(pady=5)
        self.overlay_x = tk.StringVar(value="0")
        self.overlay_y = tk.StringVar(value="0")
        self.overlay_scale = tk.StringVar(value="1.0")
        ttk.Label(overlay_frame, text="X:", bootstyle=SECONDARY).grid(row=0, column=0, padx=5)
        x_entry = ttk.Entry(overlay_frame, textvariable=self.overlay_x, width=10, bootstyle=DEFAULT)
        x_entry.grid(row=0, column=1, padx=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(x_entry)  # Add context menu
        ttk.Label(overlay_frame, text="Y:", bootstyle=SECONDARY).grid(row=0, column=2, padx=5)
        y_entry = ttk.Entry(overlay_frame, textvariable=self.overlay_y, width=10, bootstyle=DEFAULT)
        y_entry.grid(row=0, column=3, padx=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(y_entry)  # Add context menu
        ttk.Label(overlay_frame, text="Scale:", bootstyle=SECONDARY).grid(row=1, column=0, padx=5)
        scale_entry = ttk.Entry(overlay_frame, textvariable=self.overlay_scale, width=10, bootstyle=DEFAULT)
        scale_entry.grid(row=1, column=1, padx=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(scale_entry)  # Add context menu

        ttk.Label(self, text="Text Overlay:", bootstyle=SECONDARY).pack(pady=5)
        ttk.Label(self, text="Text:", bootstyle=SECONDARY).pack()
        self.overlay_text = tk.StringVar(value="")
        text_entry = ttk.Entry(self, textvariable=self.overlay_text, width=50, bootstyle=DEFAULT)
        text_entry.pack(pady=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(text_entry)  # Add context menu

        text_frame = ttk.Frame(self)
        text_frame.pack(pady=5)
        self.text_font_size = tk.StringVar(value="24")
        self.text_color = tk.StringVar(value="white")
        self.text_x = tk.StringVar(value="10")
        self.text_y = tk.StringVar(value="10")
        ttk.Label(text_frame, text="Font Size:", bootstyle=SECONDARY).grid(row=0, column=0, padx=5)
        font_size_entry = ttk.Entry(text_frame, textvariable=self.text_font_size, width=10, bootstyle=DEFAULT)
        font_size_entry.grid(row=0, column=1, padx=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(font_size_entry)  # Add context menu
        ttk.Label(text_frame, text="Color:", bootstyle=SECONDARY).grid(row=0, column=2, padx=5)
        color_entry = ttk.Entry(text_frame, textvariable=self.text_color, width=10, bootstyle=DEFAULT)
        color_entry.grid(row=0, column=3, padx=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(color_entry)  # Add context menu
        ttk.Label(text_frame, text="X:", bootstyle=SECONDARY).grid(row=1, column=0, padx=5)
        text_x_entry = ttk.Entry(text_frame, textvariable=self.text_x, width=10, bootstyle=DEFAULT)
        text_x_entry.grid(row=1, column=1, padx=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(text_x_entry)  # Add context menu
        ttk.Label(text_frame, text="Y:", bootstyle=SECONDARY).grid(row=1, column=2, padx=5)
        text_y_entry = ttk.Entry(text_frame, textvariable=self.text_y, width=10, bootstyle=DEFAULT)
        text_y_entry.grid(row=1, column=3, padx=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(text_y_entry)  # Add context menu

        ttk.Button(self, text="Apply Overlays", command=self.event_handler.apply_overlays, bootstyle=PRIMARY).pack(pady=5)