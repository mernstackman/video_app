import tkinter as tk
from ttkbootstrap import ttk
from ttkbootstrap.constants import *
import logging

class CropControlsWidget(ttk.Frame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.setup_logging()
        # Store previous values for crop inputs
        self.prev_crop_x1 = ""
        self.prev_crop_y1 = ""
        self.prev_crop_x2 = ""
        self.prev_crop_y2 = ""
        self.create_widgets()

    def setup_logging(self):
        logging.basicConfig(filename='crop_debug.log', level=logging.DEBUG,
                           format='%(asctime)s - %(levelname)s - %(message)s')

    def create_widgets(self):
        # Crop Section
        ttk.Label(self, text="Crop Settings:", bootstyle=SECONDARY).pack(pady=5)
        crop_frame = ttk.Frame(self)
        crop_frame.pack(pady=5)

        self.crop_x1 = tk.StringVar(value="")
        self.crop_y1 = tk.StringVar(value="")
        self.crop_x2 = tk.StringVar(value="")
        self.crop_y2 = tk.StringVar(value="")

        # Crop Coordinates
        ttk.Label(crop_frame, text="X1:", bootstyle=SECONDARY).grid(row=0, column=0, padx=5)
        x1_entry = ttk.Entry(crop_frame, textvariable=self.crop_x1, width=10, bootstyle=DEFAULT)
        x1_entry.grid(row=0, column=1, padx=5)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(x1_entry)
        x1_entry.bind("<FocusOut>", lambda e: self.on_crop_change("x1"))
        logging.debug("X1 entry bindings set")

        ttk.Label(crop_frame, text="Y1:", bootstyle=SECONDARY).grid(row=0, column=2, padx=5)
        y1_entry = ttk.Entry(crop_frame, textvariable=self.crop_y1, width=10, bootstyle=DEFAULT)
        y1_entry.grid(row=0, column=3, padx=5)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(y1_entry)
        y1_entry.bind("<FocusOut>", lambda e: self.on_crop_change("y1"))
        logging.debug("Y1 entry bindings set")

        ttk.Label(crop_frame, text="X2:", bootstyle=SECONDARY).grid(row=1, column=0, padx=5)
        x2_entry = ttk.Entry(crop_frame, textvariable=self.crop_x2, width=10, bootstyle=DEFAULT)
        x2_entry.grid(row=1, column=1, padx=5)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(x2_entry)
        x2_entry.bind("<FocusOut>", lambda e: self.on_crop_change("x2"))
        logging.debug("X2 entry bindings set")

        ttk.Label(crop_frame, text="Y2:", bootstyle=SECONDARY).grid(row=1, column=2, padx=5)
        y2_entry = ttk.Entry(crop_frame, textvariable=self.crop_y2, width=10, bootstyle=DEFAULT)
        y2_entry.grid(row=1, column=3, padx=5)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(y2_entry)
        y2_entry.bind("<FocusOut>", lambda e: self.on_crop_change("y2"))
        logging.debug("Y2 entry bindings set")

        # Preview Crop Button
        ttk.Button(crop_frame, text="Preview Crop", command=self.preview_crop, bootstyle=PRIMARY).grid(row=2, column=0, columnspan=4, pady=5)
        logging.debug("Preview Crop button added")

    def on_crop_change(self, field):
        """Check if crop input has changed and update the crop rectangle if necessary."""
        current_values = {
            "x1": self.crop_x1.get(),
            "y1": self.crop_y1.get(),
            "x2": self.crop_x2.get(),
            "y2": self.crop_y2.get()
        }
        prev_values = {
            "x1": self.prev_crop_x1,
            "y1": self.prev_crop_y1,
            "x2": self.prev_crop_x2,
            "y2": self.prev_crop_y2
        }

        if current_values[field] != prev_values[field]:
            logging.debug(f"Crop {field} changed: {prev_values[field]} -> {current_values[field]}")
            if self.event_handler.ui:
                self.event_handler.ui.update_preview(update_rectangle_only=True)
                logging.debug(f"Updated crop rectangle for {field}")
            else:
                logging.error("UI not set in event_handler")

        # Update previous values
        self.prev_crop_x1 = current_values["x1"]
        self.prev_crop_y1 = current_values["y1"]
        self.prev_crop_x2 = current_values["x2"]
        self.prev_crop_y2 = current_values["y2"]

    def preview_crop(self):
        """Trigger preview update for crop parameters."""
        if self.event_handler.ui:
            logging.debug(f"Preview Crop triggered: x1={self.crop_x1.get()}, y1={self.crop_y1.get()}, "
                         f"x2={self.crop_x2.get()}, y2={self.crop_y2.get()}")
            self.event_handler.ui.update_preview()
        else:
            logging.error("UI not set in event_handler")