import tkinter as tk
from ttkbootstrap import ttk
from ttkbootstrap.constants import *

class CropControlsWidget(ttk.Frame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Crop Parameters (x1, y1, x2, y2):", bootstyle=SECONDARY).pack(pady=5)
        crop_frame = ttk.Frame(self)
        crop_frame.pack(pady=5)

        self.crop_x1 = tk.StringVar(value="0")
        self.crop_y1 = tk.StringVar(value="0")
        self.crop_x2 = tk.StringVar(value="0")
        self.crop_y2 = tk.StringVar(value="0")
        self.preserve_aspect = tk.BooleanVar(value=True)

        ttk.Label(crop_frame, text="x1:", bootstyle=SECONDARY).grid(row=0, column=0, padx=5)
        x1_entry = ttk.Entry(crop_frame, textvariable=self.crop_x1, width=10, bootstyle=DEFAULT)
        x1_entry.grid(row=0, column=1, padx=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(x1_entry)  # Add context menu
        ttk.Label(crop_frame, text="y1:", bootstyle=SECONDARY).grid(row=0, column=2, padx=5)
        y1_entry = ttk.Entry(crop_frame, textvariable=self.crop_y1, width=10, bootstyle=DEFAULT)
        y1_entry.grid(row=0, column=3, padx=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(y1_entry)  # Add context menu
        ttk.Label(crop_frame, text="x2:", bootstyle=SECONDARY).grid(row=1, column=0, padx=5)
        x2_entry = ttk.Entry(crop_frame, textvariable=self.crop_x2, width=10, bootstyle=DEFAULT)
        x2_entry.grid(row=1, column=1, padx=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(x2_entry)  # Add context menu
        ttk.Label(crop_frame, text="y2:", bootstyle=SECONDARY).grid(row=1, column=2, padx=5)
        y2_entry = ttk.Entry(crop_frame, textvariable=self.crop_y2, width=10, bootstyle=DEFAULT)
        y2_entry.grid(row=1, column=3, padx=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(y2_entry)  # Add context menu

        ttk.Checkbutton(self, text="Preserve Aspect Ratio", variable=self.preserve_aspect, bootstyle=PRIMARY).pack(pady=5)

        ttk.Button(self, text="Crop Video", command=self.event_handler.crop_video, bootstyle=PRIMARY).pack(pady=5)