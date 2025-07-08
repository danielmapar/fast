import tkinter as tk
from tkinter import messagebox

from app.ui.main_window import MainWindow
from app.ui.setup_window import SetupWindow


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.withdraw()  # Hide initially to show loading screen

        try:
            self._show_loading_screen()
        except Exception as e:
            self._present_error_message(str(e))

    def _show_loading_screen(self) -> None:
        self.loading_screen = SetupWindow(
            parent=self,
            on_success_install_libraries_callback=self._on_success_install_libraries,
            on_error_install_libraries_callback=self._on_error_install_libraries,
            on_success_test_libraries_callback=self._on_success_test_libraries,
            on_error_test_libraries_callback=self._on_error_test_libraries,
            on_close_callback=self._on_close,
        )

    def _on_success_test_libraries(self) -> None:
        self.deiconify()  # Show main window
        self.main_window = MainWindow(self)

    def _on_error_test_libraries(self, error: str) -> None:
        self._present_error_message(error)

    def _on_success_install_libraries(self) -> None:
        pass

    def _on_error_install_libraries(self, error: str) -> None:
        self._present_error_message(error)

    def _on_close(self) -> None:
        self.destroy()
        self.quit()
        exit()

    def _present_error_message(self, error: str) -> None:
        messagebox.showerror("Error", str(error))
        self.destroy()
        self.quit()
        exit()
