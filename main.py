from ttkbootstrap import Window
from frontend.gui import VideoSearchDownloadUI
from frontend.event_handlers import EventHandler

if __name__ == "__main__":
    root = Window(themename="darkly")
    event_handler = EventHandler(None)
    app = VideoSearchDownloadUI(root, event_handler)
    event_handler.ui = app  # Set ui before widgets are created
    event_handler.update_video_info()
    root.mainloop()