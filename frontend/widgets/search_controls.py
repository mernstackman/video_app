import tkinter as tk
from ttkbootstrap import ttk
from ttkbootstrap.constants import *

class SearchControlsWidget(ttk.Frame):
    def __init__(self, parent, event_handler, search_queries):
        super().__init__(parent)
        self.event_handler = event_handler
        self.search_queries = search_queries
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Search Videos:", bootstyle=SECONDARY).pack(pady=5)

        self.selected_query = tk.StringVar(value="Select a query or enter custom below")
        query_combobox = ttk.Combobox(self, textvariable=self.selected_query, values=self.search_queries, width=50, state="readonly", bootstyle=DEFAULT)
        query_combobox.pack(pady=5)
        query_combobox.bind("<<ComboboxSelected>>", lambda e: self.custom_query.set(""))

        ttk.Label(self, text="Custom Query:", bootstyle=SECONDARY).pack(pady=5)
        self.custom_query = tk.StringVar()
        custom_query_entry = ttk.Entry(self, textvariable=self.custom_query, width=50, bootstyle=DEFAULT)
        custom_query_entry.pack(pady=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(custom_query_entry)  # Add context menu

        options_frame = ttk.Frame(self)
        options_frame.pack(pady=5)

        self.results_length = tk.StringVar(value="5")
        ttk.Label(options_frame, text="Number of Results:", bootstyle=SECONDARY).pack(side=LEFT, padx=5)
        results_entry = ttk.Entry(options_frame, textvariable=self.results_length, width=10, bootstyle=DEFAULT)
        results_entry.pack(side=LEFT, padx=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(results_entry)  # Add context menu

        self.max_downloads = tk.StringVar(value="1")
        ttk.Label(options_frame, text="Max Downloads:", bootstyle=SECONDARY).pack(side=LEFT, padx=5)
        downloads_entry = ttk.Entry(options_frame, textvariable=self.max_downloads, width=10, bootstyle=DEFAULT)
        downloads_entry.pack(side=LEFT, padx=5)
        if self.event_handler.ui:  # Check if ui is set
            self.event_handler.ui.add_context_menu(downloads_entry)  # Add context menu

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="Search", command=self.event_handler.search_videos, bootstyle=PRIMARY).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Download Next", command=self.event_handler.download_videos, bootstyle=PRIMARY).pack(side=LEFT, padx=5)