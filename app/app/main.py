from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, messagebox
from app.lambda_thread import LambdaThread
from app.command_manager import CommandManager
from app.logger import get_logger

load_dotenv()

logger = get_logger()
logger.info("Starting Fast App...")
logger.configure()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.logger = get_logger()

        # Hide the main window
        self.withdraw()

        try:
            self.command_manager = CommandManager()
        except Exception as e:
            self.present_error_message(e)

        self.setup_loading_screen()
    
    def present_error_message(self, error):
        messagebox.showerror("Error", str(error))
        self.destroy()
        self.quit()
        exit()
    
    def setup_loading_screen(self):
        # Create a loading screen
        self.loading_screen = tk.Toplevel(self)
        self.loading_screen.title("Fast App Setup")
        self.loading_screen.geometry("300x100")
        self.loading_screen.configure(bg='#FFFFFF')

        # Create a label in the loading screen
        label = tk.Label(self.loading_screen, text="Installing libraries...", font=('Arial', 16))
        label.pack(expand=True)

        # Create a progress bar in the loading screen
        self.progress_bar = ttk.Progressbar(self.loading_screen, orient="horizontal", length=300, mode="indeterminate")
        self.progress_bar.pack(expand=True)

        # Start the progress bar
        self.progress_bar.start(10)
        
        # Create and start the thread with lambda function
        setup_thread = LambdaThread(
            target_function=lambda: self.command_manager.setup_and_test_libraries(),
            on_success=lambda result: self.after(0, self.on_setup_success),
            on_error=lambda error: self.after(0, lambda: self.on_setup_error(error))
        )
        setup_thread.start()

    def on_setup_success(self):
        """Called when library setup succeeds - runs on main thread"""
        logger.info("Libraries setup completed successfully")
        self.progress_bar.stop()
        self.loading_screen.destroy()

        # Create the tabbed interface
        self.create_app_main_screen()
    
    def on_setup_error(self, error):
        """Called when library setup fails - runs on main thread"""
        self.progress_bar.stop()
        self.loading_screen.destroy()
        self.present_error_message(error)

    def setup_frame_for_fastqc(self, frame):
        
        self.fastqc_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.fastqc_frame, text='FastQC')

        # Create a label in the frame
        label = tk.Label(self.fastqc_frame, text="FastQC", font=('Arial', 16))
        label.pack(expand=True)
    
    def setup_frame_for_fastp(self, frame):
        
        self.fastp_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.fastp_frame, text='FastP')

        # Create a label in the frame
        label = tk.Label(self.fastp_frame, text="FastP", font=('Arial', 16))
        label.pack(expand=True)
    
    def setup_frame_for_hybpiper(self, frame):
        
        self.hybpiper_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hybpiper_frame, text='HybPiper')

        # Create a label in the frame
        label = tk.Label(self.hybpiper_frame, text="HybPiper", font=('Arial', 16))
        label.pack(expand=True)
    
    def create_app_main_screen(self):
        # Show the main window
        self.deiconify()

        self.title("Fast App")
        self.minsize(1200, 800)
        self.maxsize(1200, 800)        
        
        self.center_window()
        
        # Try these alternative background configurations
        self.configure(bg='#FFFFFF')  # Use hex instead of color name

        # Create and configure style for bigger tabs
        style = ttk.Style()
        style.configure('TNotebook.Tab', 
                       padding=[20, 10],  # [horizontal, vertical] padding
                       font=('Arial', 12, 'bold'))  # Bigger font
        
        # Create notebook widget for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create Tab 1 (FastQC)
        self.setup_frame_for_fastqc(self.notebook)
        
        # Create Tab 2 (FastP)
        self.setup_frame_for_fastp(self.notebook)
        
        # Create Tab 3 (HybPiper)
        self.setup_frame_for_hybpiper(self.notebook)

    def center_window(self):
        self.update_idletasks()
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = self.winfo_width()
        window_height = self.winfo_height()

        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)

        self.geometry(f"+{position_x}+{position_y}")

def run_gui():
    app = App()
    app.mainloop()

def main():
    run_gui()
    
if __name__ == "__main__":
    run_gui() 