import tkinter.ttk as ttk


class BaseToolFrame:
    def __init__(self, notebook, tab_name):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=tab_name)
        self.setup_frame()

    def setup_frame(self):
        """Override this method in subclasses"""
        pass
