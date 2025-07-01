from dotenv import load_dotenv
import os
import tkinter as tk
from tkinter import ttk
import shutil
from app.library_downloader import LibraryDownloader
from app.library_runner import LibraryRunner

load_dotenv()

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Fast App")
        self.minsize(1200, 800)
        self.maxsize(1200, 800)
        
        # Try these alternative background configurations
        self.configure(bg='#FFFFFF')  # Use hex instead of color name
        
        # Force window update and center it
        self.update_idletasks()
        self.center_window()
        
        # Create the tabbed interface
        self.create_menu_tabs()
    
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
    
    def create_menu_tabs(self):
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

    download_dir = os.path.expanduser("~/.fast-app")
    jdk_path = os.path.join(download_dir, "amazon-corretto-21")
    fastqc_path = os.path.join(download_dir, "fastqc_v0.12.1")
    perl_path = os.path.join(download_dir, "perl-5.40.0")

    # Download all libraries (fastqc, fastp, hybpiper)
    library_downloader = LibraryDownloader(download_dir, jdk_path, fastqc_path, perl_path)
    library_runner = LibraryRunner(jdk_path, fastqc_path, perl_path)
    try:
        library_downloader.setup_all_libraries()
    except Exception as e:
        print(f"Error: {e}")
        return 

    try:
        library_runner.test_all_libraries()
    except Exception as e:
        print(f"Error while testing installations: {e}")
        return

    app = App()
    app.mainloop()

def main():
    run_gui()
    
if __name__ == "__main__":
    run_gui()