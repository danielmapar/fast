import tkinter as tk
from tkinter import messagebox
import logging
import dotenv
from app.library.manager import LibraryManager
from app.ui.loading_screen import LoadingScreen
from app.ui.main_window import MainWindow
from app.logger.config import setup_logger

dotenv.load_dotenv()

setup_logger()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger()
        self.withdraw()  # Hide initially
        
        try:
            self.show_loading_screen()
        except Exception as e:
            self.present_error_message(e)
    
    def show_loading_screen(self):
        self.loading_screen = LoadingScreen(
            parent=self,
            on_success=self.on_setup_success,
            on_error=self.on_setup_error,
            on_cancel=self.on_setup_cancel
        )
    
    def on_setup_success(self):
        self.deiconify()  # Show main window
        self.main_window = MainWindow(self)
    
    def on_setup_error(self, error):
        self.present_error_message(error)
    
    def on_setup_cancel(self):
        self.destroy()
        self.quit()
    
    def present_error_message(self, error):
        messagebox.showerror("Error", str(error))
        self.destroy()
        self.quit()
        exit()

def run_gui():
    app = App()
    app.mainloop()

def main():
    run_gui()

if __name__ == "__main__":
    run_gui()