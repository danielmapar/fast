import tkinter.ttk as ttk


class AppStyles:
    @staticmethod
    def setup_notebook_style():
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[20, 10], font=("Arial", 12, "bold"))
        return style
