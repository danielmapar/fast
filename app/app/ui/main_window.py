import tkinter.ttk as ttk
from app.ui.styles import AppStyles
from app.ui.tool_frames import FastQCFrame, FastPFrame, HybPiperFrame

class MainWindow:
    def __init__(self, parent):
        self.parent = parent
        self.setup_window()
        self.setup_styling()
        self.create_tabs()
    
    def setup_window(self):
        self.parent.title("Fast App")
        self.parent.minsize(1200, 800)
        self.parent.maxsize(1200, 800)
        self.parent.configure(bg='#FFFFFF')
        self.center_window()
    
    def setup_styling(self):
        self.style = AppStyles.setup_notebook_style()
    
    def create_tabs(self):
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tool frames
        self.fastqc_frame = FastQCFrame(self.notebook)
        self.fastp_frame = FastPFrame(self.notebook)
        self.hybpiper_frame = HybPiperFrame(self.notebook)
    
    def center_window(self):
        self.parent.update_idletasks()
        
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        window_width = self.parent.winfo_width()
        window_height = self.parent.winfo_height()
        
        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)
        
        self.parent.geometry(f"+{position_x}+{position_y}")