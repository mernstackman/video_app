import tkinter as tk
from ttkbootstrap import ttk
from ttkbootstrap.constants import *
from tkinter import colorchooser
import logging

class TextControlsWidget(ttk.Frame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.setup_logging()
        self.create_widgets()

    def setup_logging(self):
        logging.basicConfig(filename='crop_debug.log', level=logging.DEBUG,
                           format='%(asctime)s - %(levelname)s - %(message)s')

    def create_widgets(self):
        # Text Overlay Section
        ttk.Label(self, text="Text Overlay:", bootstyle=SECONDARY).pack(pady=5)
        text_frame = ttk.Frame(self)
        text_frame.pack(pady=5)

        self.overlay_text = tk.StringVar(value="")
        self.text_x = tk.StringVar(value="10")
        self.text_y = tk.StringVar(value="10")
        self.text_font_size = tk.StringVar(value="24")
        self.text_color = tk.StringVar(value="white")
        self.text_font = tk.StringVar(value="arial.ttf")
        self.text_opacity = tk.StringVar(value="1.0")

        # Text Input
        ttk.Label(text_frame, text="Text:", bootstyle=SECONDARY).grid(row=0, column=0, padx=5)
        text_entry = ttk.Entry(text_frame, textvariable=self.overlay_text, width=20, bootstyle=DEFAULT)
        text_entry.grid(row=0, column=1, padx=5, columnspan=3)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(text_entry)
        logging.debug("Text entry bindings set")

        # Font Selector
        ttk.Label(text_frame, text="Font:", bootstyle=SECONDARY).grid(row=1, column=0, padx=5)
        font_options = ["arial.ttf", "times.ttf", "helvR.ttf", "cour.ttf", "verdana.ttf"]
        font_combobox = ttk.Combobox(text_frame, textvariable=self.text_font, values=font_options, state="readonly", width=17)
        font_combobox.grid(row=1, column=1, padx=5)
        font_combobox.set(font_options[0])
        logging.debug("Font combobox binding set")

        # Font Size
        ttk.Label(text_frame, text="Font Size:", bootstyle=SECONDARY).grid(row=1, column=2, padx=5)
        font_size_entry = ttk.Entry(text_frame, textvariable=self.text_font_size, width=10, bootstyle=DEFAULT)
        font_size_entry.grid(row=1, column=3, padx=5)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(font_size_entry)
        logging.debug("Font size entry bindings set")

        # Color Selector
        ttk.Label(text_frame, text="Color:", bootstyle=SECONDARY).grid(row=2, column=0, padx=5)
        color_entry = ttk.Entry(text_frame, textvariable=self.text_color, width=10, bootstyle=DEFAULT)
        color_entry.grid(row=2, column=1, padx=5)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(color_entry)
        ttk.Button(text_frame, text="Pick Color", command=self.pick_color, bootstyle=PRIMARY).grid(row=2, column=2, padx=5)
        logging.debug("Color entry bindings set")

        # Position (X, Y) and Opacity
        ttk.Label(text_frame, text="X:", bootstyle=SECONDARY).grid(row=3, column=0, padx=5)
        x_entry = ttk.Entry(text_frame, textvariable=self.text_x, width=10, bootstyle=DEFAULT)
        x_entry.grid(row=3, column=1, padx=5)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(x_entry)
        logging.debug("X position entry bindings set")

        ttk.Label(text_frame, text="Y:", bootstyle=SECONDARY).grid(row=3, column=2, padx=5)
        y_entry = ttk.Entry(text_frame, textvariable=self.text_y, width=10, bootstyle=DEFAULT)
        y_entry.grid(row=3, column=3, padx=5)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(y_entry)
        logging.debug("Y position entry bindings set")

        ttk.Label(text_frame, text="Opacity (0-1):", bootstyle=SECONDARY).grid(row=4, column=0, padx=5)
        opacity_entry = ttk.Entry(text_frame, textvariable=self.text_opacity, width=10, bootstyle=DEFAULT)
        opacity_entry.grid(row=4, column=1, padx=5)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(opacity_entry)
        logging.debug("Opacity entry bindings set")

        # Preview Text Overlay Button
        ttk.Button(text_frame, text="Preview Text Overlay", command=self.preview_text_overlay, bootstyle=PRIMARY).grid(row=4, column=2, columnspan=2, pady=5)
        logging.debug("Preview Text Overlay button added")

    def pick_color(self):
        """Open a color picker dialog and set the selected color."""
        color = colorchooser.askcolor(title="Select Text Color")[1]  # Returns (RGB, hex)
        if color:
            self.text_color.set(color)
            logging.debug(f"Color picked: {color}")

    def preview_text_overlay(self):
        """Trigger preview update for text overlay parameters."""
        if self.event_handler.ui:
            logging.debug(f"Preview Text Overlay triggered: text={self.overlay_text.get()}, font={self.text_font.get()}, "
                         f"size={self.text_font_size.get()}, color={self.text_color.get()}, "
                         f"x={self.text_x.get()}, y={self.text_y.get()}, opacity={self.text_opacity.get()}")
            self.event_handler.ui.update_preview()
        else:
            logging.error("UI not set in event_handler")