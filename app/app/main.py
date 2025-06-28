from dotenv import load_dotenv

import asyncio

import tkinter as tk
from tkinter import ttk
import asyncio
import time
import os

load_dotenv()

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Fast App")
        self.minsize(350, 200)
        self.center_window()

        self.main_label = ttk.Label(
            self,
            text="Hello, World!",
            font=("Helvetica", 16, "bold")
        )
        self.main_label.pack(expand=True, padx=20, pady=10)

        self.time_label = ttk.Label(
            self,
            text="Waiting for async update...",
            font=("Helvetica", 12)
        )
        self.time_label.pack(expand=True, padx=20, pady=10)

    def center_window(self):
        self.update_idletasks()
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = self.winfo_width()
        window_height = self.winfo_height()

        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)

        # Set the window's position
        self.geometry(f"+{position_x}+{position_y}")

async def update_time(app):
    while True:
        if not app.winfo_exists():
            break
        
        current_time = time.strftime("%H:%M:%S")
        app.time_label.config(text=f"Current Time: {current_time}")
        
        # await asyncio.sleep() gives control back to the event loop for a
        # specified duration, allowing other tasks to run.
        await asyncio.sleep(1)


async def run_gui():
    """Run the app with GUI"""
    app = App()
    asyncio.create_task(update_time(app))

    while True:
        try:
            app.update()
            app.update_idletasks()
        except tk.TclError:
            break
        
        await asyncio.sleep(0.01)

async def run():
    try:
        await run_gui()
    except tk.TclError as e:
        print(f"GUI failed to start: {e}")


def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Application closed by user.")


if __name__ == "__main__":
    main()