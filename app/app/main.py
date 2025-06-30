from dotenv import load_dotenv
import asyncio
import tkinter as tk
from tkinter import ttk
import time
import os

load_dotenv()

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Fast App")
        self.minsize(800, 600)
        
        # Try these alternative background configurations
        self.configure(bg='#FFFFFF')  # Use hex instead of color name
        
        # Force window update and center it
        self.update_idletasks()
        self.center_window()
        
        # Add a simple widget to verify rendering
        label = tk.Label(self, text="Hello World!", bg='white', fg='black', font=('Arial', 20))
        label.pack(expand=True)

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