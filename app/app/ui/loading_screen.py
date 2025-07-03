import tkinter as tk
import tkinter.ttk as ttk
import logging
from app.thread.lambda_runner import LambdaThreadRunner
from app.library.manager import LibraryManager

class LoadingScreen:
    def __init__(self, parent, on_success, on_error, on_cancel):
        self.parent = parent
        self.on_success = on_success
        self.on_error = on_error
        self.on_cancel = on_cancel
        self.logger = logging.getLogger()
        
        self.setup_window()
        self.start_setup()
    
    def setup_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Fast App Setup")
        self.window.geometry("300x100")
        self.window.configure(bg='#FFFFFF')
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Setup progress bar and label
        label = tk.Label(self.window, text="Installing libraries...", font=('Arial', 16))
        label.pack(expand=True)
        
        self.progress_bar = ttk.Progressbar(self.window, orient="horizontal", length=300, mode="indeterminate")
        self.progress_bar.pack(expand=True)
        self.progress_bar.start(10)
    
    def start_setup(self):
        self.setup_thread = LambdaThreadRunner(
            target_function=lambda: LibraryManager().setup_and_test_libraries(),
            on_success=lambda result: self.parent.after(0, self.on_setup_success),
            on_error=lambda error: self.parent.after(0, lambda: self.on_setup_error(error))
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