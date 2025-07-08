import tkinter.ttk as ttk


class BaseHardwareMonitoringFrame:
    def __init__(self, notebook: ttk.Notebook, tab_name: str) -> None:
        self._notebook = notebook
        self._frame = ttk.Frame(self._notebook)
        self._notebook.add(self._frame, text=tab_name)
        self.setup_frame()

    def setup_frame(self) -> None:
        """Override this method in subclasses"""
        pass
