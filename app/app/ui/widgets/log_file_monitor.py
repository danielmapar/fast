import os
import threading
import time
import tkinter as tk
from typing import Any, Optional, Union


class LogFileMonitor(tk.Frame):
    """
    A reusable UI component that monitors a log file and displays its contents
    in real-time with a black background and white text.
    """

    def __init__(
        self,
        parent: Union[tk.Frame, tk.Toplevel, tk.Widget],
        file_path: Optional[str] = None,
        height: int = 10,
        width: int = 100,
        title: str = "Log Monitor",
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)

        self._parent = parent
        self._current_file_path = file_path
        self._last_file_size = 0
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._title_text = title
        self._content_visible = True  # Track visibility state

        # Initialize UI components - these will be set in _setup_ui()
        self._content_frame: tk.Frame
        self._title_frame: tk.Frame
        self._title_button: tk.Button
        self._text_widget: tk.Text

        self._setup_ui(height, width)

        if file_path:
            self._start_monitoring()

    def _setup_ui(self, height: int, width: int) -> None:
        """Set up the UI components with dark theme"""
        # Configure the frame - initially use parent's background
        parent_bg = (
            self._parent.cget("bg")
            if hasattr(self._parent, "cget")
            else "SystemButtonFace"
        )
        self.configure(bg=parent_bg)

        # Create title frame
        self._title_frame = tk.Frame(self, bg=parent_bg)
        self._title_frame.pack(fill=tk.X, pady=(0, 2))

        # Create clickable title button
        self._title_button = tk.Button(
            self._title_frame,
            text=f"▼ {self._title_text}",
            bg="#333333",
            fg="white",
            relief=tk.FLAT,
            font=("Arial", 10, "bold"),
            anchor="w",
            command=self._toggle_content,
        )
        self._title_button.pack(fill=tk.X)

        # Create content frame to hold scrollbar and text widget
        self._content_frame = tk.Frame(self, bg="black")
        self._content_frame.pack(fill=tk.BOTH, expand=True)

        # Create scrollbar
        scrollbar = tk.Scrollbar(self._content_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create text widget with dark theme
        self._text_widget = tk.Text(
            self._content_frame,
            height=height,
            width=width,
            bg="black",
            fg="white",
            insertbackground="white",  # Cursor color
            selectbackground="gray",  # Selection background
            selectforeground="white",  # Selection text color
            font=("Consolas", 9),  # Monospace font for logs
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
        )
        self._text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbar
        scrollbar.config(command=self._text_widget.yview)

        # Insert placeholder text
        self._text_widget.insert("1.0", "No log file specified...")
        self._text_widget.config(state=tk.DISABLED)  # Make read-only

    def _toggle_content(self) -> None:
        """Toggle the visibility of the log content"""
        if self._content_visible:
            # Hide content
            self._content_frame.pack_forget()
            self._title_button.config(text=f"▶ {self._title_text}")
            self._content_visible = False
            # Change background to parent's background to avoid black box
            parent_bg = (
                self._parent.cget("bg")
                if hasattr(self._parent, "cget")
                else "SystemButtonFace"
            )
            self.configure(bg=parent_bg)
        else:
            # Show content
            self._content_frame.pack(fill=tk.BOTH, expand=True)
            self._title_button.config(text=f"▼ {self._title_text}")
            self._content_visible = True
            # Restore black background when content is visible
            self.configure(bg="black")

    def _set_title(self, title: str) -> None:
        """Update the title text"""
        self._title_text = title
        arrow = "▼" if self._content_visible else "▶"
        self._title_button.config(text=f"{arrow} {self._title_text}")

    def set_file_path(self, file_path: str) -> None:
        """Change the file being monitored"""
        # Stop current monitoring
        self._stop_monitoring()

        # Update file path and reset
        self._current_file_path = file_path
        self._last_file_size = 0

        # Update title to show file name if available
        # if file_path:
        #     filename = os.path.basename(file_path)
        #     self._set_title(f"Log Monitor - {filename}")
        # else:
        self._set_title("Log Monitor")

        # Clear the display
        self._clear_display()

        # Start monitoring the new file
        if file_path:
            self._start_monitoring()
        else:
            self._text_widget.config(state=tk.NORMAL)
            self._text_widget.insert("1.0", "No log file specified...")
            self._text_widget.config(state=tk.DISABLED)

    def _start_monitoring(self) -> None:
        """Start monitoring the current file for changes"""
        if not self._current_file_path or self._monitoring_active:
            return

        self._monitoring_active = True

        # Load existing content if file exists
        if os.path.exists(self._current_file_path):
            try:
                with open(self._current_file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content.strip():

                        def update_func() -> None:
                            self._update_display(content, replace=True)

                        self._parent.after(0, update_func)
                    self._last_file_size = len(content.encode("utf-8"))
            except Exception as e:
                error_str = str(e)

                def error_func() -> None:
                    self._update_display(
                        f"Error reading file: {error_str}\n", replace=True
                    )

                self._parent.after(0, error_func)

        # Start monitoring thread
        self._monitor_thread = threading.Thread(target=self._monitor_file, daemon=True)
        self._monitor_thread.start()

    def _stop_monitoring(self) -> None:
        """Stop monitoring the current file"""
        self._monitoring_active = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)

    def _clear_display(self) -> None:
        """Clear the text display"""
        self._text_widget.config(state=tk.NORMAL)
        self._text_widget.delete("1.0", tk.END)
        self._text_widget.config(state=tk.DISABLED)

    def _monitor_file(self) -> None:
        """Background thread function to monitor file changes"""
        while self._monitoring_active:
            try:
                if self._current_file_path and os.path.exists(self._current_file_path):
                    current_size = os.path.getsize(self._current_file_path)

                    if current_size > self._last_file_size:
                        # File has grown, read the new content
                        with open(self._current_file_path, "r", encoding="utf-8") as f:
                            f.seek(self._last_file_size)
                            new_content = f.read()

                            if new_content.strip():
                                if len(new_content) == 0:
                                    continue

                                # Schedule GUI update on main thread
                                def update_func(content=new_content) -> None:
                                    self._update_display(content)

                                self._parent.after(0, update_func)

                            self._last_file_size = current_size
                    elif current_size < self._last_file_size:
                        # File was truncated or recreated, reload from beginning
                        self._last_file_size = 0

                        def clear_func() -> None:
                            self._clear_display()

                        self._parent.after(0, clear_func)

                time.sleep(0.5)  # Check every 500ms

            except Exception as e:
                error_str = str(e)

                def error_func(error_message=error_str) -> None:
                    self._update_display(f"Error monitoring file: {error_message}\n")

                self._parent.after(0, error_func)
                time.sleep(1)

    def _update_display(self, content: str, replace: bool = False) -> None:
        """Update the text widget with new content (called on main thread)"""
        try:
            self._text_widget.config(state=tk.NORMAL)

            if replace:
                # Replace all content
                self._text_widget.delete("1.0", tk.END)
                self._text_widget.insert("1.0", content)
            else:
                # Check if we need to clear placeholder text
                current_content = self._text_widget.get("1.0", "end-1c")
                if current_content in ["No log file specified...", ""]:
                    self._text_widget.delete("1.0", tk.END)

                # Append new content
                self._text_widget.insert(tk.END, content)

            # Auto-scroll to bottom
            self._text_widget.see(tk.END)
            self._text_widget.config(state=tk.DISABLED)

        except Exception as e:
            raise Exception(f"Error updating display: {e}")

    def destroy(self) -> None:
        """Clean up when destroying the widget"""
        self._stop_monitoring()
        super().destroy()
