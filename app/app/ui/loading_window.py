import tkinter as tk
import tkinter.ttk as ttk
from typing import Callable, Optional

from app.library.manager import LibraryManager
from app.logger.config import Logger, LogType
from app.thread.lambda_runner import LambdaThreadRunner
from app.ui.utils import WindowUtils
from app.ui.widget.log_file_monitor import LogFileMonitor


class LoadingWindow:
    def __init__(
        self,
        parent: tk.Tk,
        on_success_install_libraries_callback: Callable[[], None],
        on_error_install_libraries_callback: Callable[[str], None],
        on_success_test_libraries_callback: Callable[[], None],
        on_error_test_libraries_callback: Callable[[str], None],
        on_close_callback: Callable[[], None],
    ) -> None:
        self._parent = parent

        # UI elements
        self._status_label: Optional[tk.Label] = None
        self._logo: Optional[tk.Label] = None
        self._progress_bar: Optional[ttk.Progressbar] = None
        self._window: Optional[tk.Toplevel] = None
        self._log_monitor_panel: Optional[LogFileMonitor] = None

        # Callbacks
        self._on_success_install_libraries_callback = (
            on_success_install_libraries_callback
        )
        self._on_error_install_libraries_callback = on_error_install_libraries_callback
        self._on_success_test_libraries_callback = on_success_test_libraries_callback
        self._on_error_test_libraries_callback = on_error_test_libraries_callback
        self._on_close_callback = on_close_callback

        # Library manager
        self._library_manager = LibraryManager()

        # Threads
        self._install_libraries_thread: Optional[LambdaThreadRunner] = None
        self._test_libraries_thread: Optional[LambdaThreadRunner] = None

        # Log files
        self._installing_log_file = Logger().get_log_file_path(
            LogType.INSTALLING_LIBRARIES
        )
        self._testing_log_file = Logger().get_log_file_path(LogType.TESTING_LIBRARIES)

        # Setup window
        self._setup_window()
        self._start_install_libraries()

    def _setup_window(self) -> None:
        self._window = tk.Toplevel(self._parent)
        self._window.title("Fast App Setup")
        self._window.configure(bg="#FFFFFF")
        self._window.protocol("WM_DELETE_WINDOW", self._handle_close)

        WindowUtils.setup_logo(self._window)
        self._setup_progress_bar()
        self._setup_logs_pannel()
        WindowUtils.center_window(self._window)

    def _setup_progress_bar(self) -> None:
        # Setup progress bar and label
        self._status_label = tk.Label(
            self._window, text="Loading...", font=("Arial", 12, "bold"), bg="#FFFFFF"
        )
        self._status_label.pack(expand=True)

        self._progress_bar = ttk.Progressbar(
            self._window, orient="horizontal", length=300, mode="indeterminate"
        )
        self._progress_bar.pack(expand=True)
        self._progress_bar.start(10)

    def _setup_logs_pannel(self) -> None:
        if self._window:
            self._log_monitor_panel = LogFileMonitor(
                self._window, file_path=self._installing_log_file, height=12, width=100
            )
            self._log_monitor_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def _update_status_label(self, text: str) -> None:
        if self._status_label:
            self._status_label.config(text=text)
        if self._window:
            WindowUtils.center_window(self._window)

    def _start_install_libraries(self) -> None:
        self._update_status_label("Installing libraries...")
        self._install_libraries_thread = LambdaThreadRunner(
            target_function=lambda: self._library_manager.install_libraries(),
            on_success=lambda result: self._parent.after(
                0, self._on_success_install_libraries
            ),
            on_error=lambda error: self._parent.after(
                0, lambda: self._on_error_install_libraries(error)
            ),
        )
        self._install_libraries_thread.start()

    def _start_test_libraries(self) -> None:
        self._update_status_label("Validating installed libraries...")

        # Switch the log monitor to track the testing log file
        if self._log_monitor_panel:
            self._log_monitor_panel.set_file_path(self._testing_log_file)

        self._test_libraries_thread = LambdaThreadRunner(
            target_function=lambda: self._library_manager.test_libraries(),
            on_success=lambda result: self._parent.after(
                0, self._on_success_test_libraries
            ),
            on_error=lambda error: self._parent.after(
                0, lambda: self._on_error_test_libraries(error)
            ),
        )
        self._test_libraries_thread.start()

    def _handle_close(self) -> None:
        self._destroy_window()
        self._on_close_callback()

    def _on_success_test_libraries(self) -> None:
        self._destroy_window()
        self._on_success_test_libraries_callback()

    def _on_error_test_libraries(self, error: str) -> None:
        self._destroy_window()
        self._on_error_test_libraries_callback(error)

    def _on_success_install_libraries(self) -> None:
        self._on_success_install_libraries_callback()
        self._start_test_libraries()

    def _on_error_install_libraries(self, error: str) -> None:
        self._destroy_window()
        self._on_error_install_libraries_callback(error)

    def _destroy_window(self) -> None:
        # Join threads if they exist and are still alive
        if self._install_libraries_thread is not None:
            self._install_libraries_thread.join(timeout=1.0)

        if self._test_libraries_thread is not None:
            self._test_libraries_thread.join(timeout=1.0)

        if self._log_monitor_panel is not None:
            self._log_monitor_panel.destroy()

        if self._progress_bar is not None:
            self._progress_bar.stop()

        if self._window is not None:
            self._window.destroy()
