import tkinter as tk
from ttkbootstrap import ttk
from ttkbootstrap.constants import *
import logging

class SoundControlsWidget(ttk.Frame):
    def __init__(self, parent, event_handler):
        super().__init__(parent)
        self.event_handler = event_handler
        self.setup_logging()
        self.create_widgets()

    def setup_logging(self):
        logging.basicConfig(filename='crop_debug.log', level=logging.DEBUG,
                           format='%(asctime)s - %(levelname)s - %(message)s')

    def create_widgets(self):
        # Sound Editing Section
        ttk.Label(self, text="Sound Settings:", bootstyle=SECONDARY).pack(pady=5)
        sound_frame = ttk.Frame(self)
        sound_frame.pack(pady=5)

        self.volume = tk.StringVar(value="1.0")

        # Volume Input
        ttk.Label(sound_frame, text="Volume (0.0-2.0):", bootstyle=SECONDARY).grid(row=0, column=0, padx=5)
        volume_entry = ttk.Entry(sound_frame, textvariable=self.volume, width=10, bootstyle=DEFAULT)
        volume_entry.grid(row=0, column=1, padx=5)
        if self.event_handler.ui:
            self.event_handler.ui.add_context_menu(volume_entry)
        logging.debug("Volume entry bindings set")

        # Preview Sound Button
        ttk.Button(sound_frame, text="Preview Sound", command=self.preview_sound, bootstyle=PRIMARY).grid(row=1, column=0, columnspan=2, pady=5)
        logging.debug("Preview Sound button added")

    def preview_sound(self):
        """Trigger preview update for sound parameters."""
        if self.event_handler.ui:
            logging.debug(f"Preview Sound triggered: volume={self.volume.get()}")
            self.event_handler.ui.update_preview()
        else:
            logging.error("UI not set in event_handler")