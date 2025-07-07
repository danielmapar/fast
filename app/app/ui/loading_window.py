import logging
import tkinter as tk
import tkinter.ttk as ttk

from PIL import Image, ImageTk

from app.library.manager import LibraryManager
from app.resource.manager import open_image
from app.thread.lambda_runner import LambdaThreadRunner


class LoadingWindow:
    def __init__(self, parent, on_success, on_error, on_cancel):
        self.parent = parent
        self.on_success = on_success
        self.on_error = on_error
        self.on_cancel = on_cancel
        self.logger = logging.getLogger()

        self.setup_window()
        self.start_setup()

    def setup_logo(self):
        try:
            logo_image = open_image("images/logo.png")
            # Resize logo to fit nicely in the window
            logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)

            logo_label = tk.Label(self.window, image=self.logo_photo, bg="#FFFFFF")
            logo_label.pack(pady=(10, 5))
        except Exception as e:
            self.logger.warning(f"Could not load logo: {e}")
            # Don't exit the entire app, just continue without logo

    def setup_progress_bar(self):
        # Setup progress bar and label
        label = tk.Label(
            self.window, text="Installing libraries...", font=("Arial", 16)
        )
        label.pack(expand=True)

        self.progress_bar = ttk.Progressbar(
            self.window, orient="horizontal", length=300, mode="indeterminate"
        )
        self.progress_bar.pack(expand=True)
        self.progress_bar.start(10)

    def setup_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Fast App Setup")
        self.window.configure(bg="#FFFFFF")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Setup logo
        self.setup_logo()

        # Setup progress bar
        self.setup_progress_bar()

        # Center window
        self.center_window()

    def center_window(self):
        self.window.update_idletasks()

        # Use reqwidth/reqheight to get the calculated required size
        width = self.window.winfo_reqwidth()
        height = self.window.winfo_reqheight()

        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Calculate center position relative to screen
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Ensure window doesn't go off screen
        x = max(0, x)
        y = max(0, y)

        self.window.geometry(f"{width}x{height}+{x}+{y}")

        # Bring window to front
        self.window.lift()
        self.window.focus_force()

    def start_setup(self):
        self.setup_thread = LambdaThreadRunner(
            target_function=lambda: LibraryManager().setup_and_test_libraries(),
            on_success=lambda result: self.parent.after(0, self.on_setup_success),
            on_error=lambda error: self.parent.after(
                0, lambda: self.on_setup_error(error)
            ),
        )
        self.setup_thread.start()

    def on_close(self):
        self.progress_bar.stop()
        self.window.destroy()
        self.on_cancel()

    def on_setup_success(self):
        self.progress_bar.stop()
        self.window.destroy()
        self.on_success()

    def on_setup_error(self, error):
        self.progress_bar.stop()
        self.window.destroy()
        self.on_error(error)
