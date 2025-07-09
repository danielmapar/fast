import platform
import queue
import threading
import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Dict, List, Optional


class BaseFrame:
    def __init__(self, notebook: ttk.Notebook, tab_name: str) -> None:
        self._notebook = notebook
        self._frame = ttk.Frame(self._notebook)
        self._notebook.add(self._frame, text=tab_name)

        # Initialize scrollable frame components
        self._canvas: Optional[tk.Canvas] = None
        self._scrollbar: Optional[ttk.Scrollbar] = None
        self._scrollable_frame: Optional[tk.Frame] = None

        # Threading components for non-blocking updates
        self._update_thread: Optional[threading.Thread] = None
        self._update_queue: queue.Queue = queue.Queue()
        self._stop_updates = threading.Event()
        self._thread_running = False

        # Windows-specific performance optimizations
        self._is_windows = platform.system() == "Windows"
        self._pending_updates: Dict[str, Any] = {}  # Batch updates for Windows
        self._update_batch_timer: Optional[str] = None

        self._setup_scrollable_frame()
        self.setup_frame()

    def _setup_scrollable_frame(self) -> None:
        """Setup scrollable canvas and frame with Windows optimizations"""
        # Create canvas and scrollbar with Windows-specific settings
        canvas_config: Dict[str, Any] = {"highlightthickness": 0}
        if self._is_windows:
            # Windows-specific optimizations - use system default background
            canvas_config.update(
                {
                    "relief": "flat",
                    "borderwidth": "0",
                    "background": "SystemButtonFace",  # Windows system default background
                }
            )

        self._canvas = tk.Canvas(self._frame, **canvas_config)
        self._scrollbar = ttk.Scrollbar(
            self._frame, orient="vertical", command=self._canvas.yview
        )

        # Frame configuration for Windows
        frame_config: Dict[str, Any] = {}
        if self._is_windows:
            frame_config["relief"] = "flat"

        self._scrollable_frame = tk.Frame(self._canvas, **frame_config)

        # Configure scrolling with Windows optimizations
        if self._is_windows:
            # Reduce scroll events on Windows
            self._scrollable_frame.bind(
                "<Configure>",
                lambda e: self._frame.after_idle(
                    lambda: (
                        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
                        if self._canvas
                        else None
                    )
                ),
            )
        else:
            self._scrollable_frame.bind(
                "<Configure>",
                lambda e: (
                    self._canvas.configure(scrollregion=self._canvas.bbox("all"))
                    if self._canvas
                    else None
                ),
            )

        self._canvas.create_window((0, 0), window=self._scrollable_frame, anchor="nw")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        # Pack canvas and scrollbar
        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.pack(side="right", fill="y")

        # Setup scrolling and resizing
        self._setup_scrolling()
        self._setup_resizing()

    def _setup_scrolling(self) -> None:
        """Setup mousewheel scrolling with cross-platform support"""
        if not self._canvas:
            return

        def on_mousewheel(event):
            # Platform-specific scroll calculation
            if platform.system() == "Windows":
                delta = int(-1 * (event.delta / 120))
            elif platform.system() == "Darwin":  # macOS
                delta = int(-1 * event.delta)
            else:  # Linux
                delta = -1 if event.num == 4 else 1 if event.num == 5 else 0

            if self._canvas:
                self._canvas.yview_scroll(delta, "units")
            return "break"  # Prevent event from propagating

        def bind_mousewheel(event):
            """Bind global mousewheel events when mouse enters the frame"""
            if self._canvas:
                self._canvas.bind_all("<MouseWheel>", on_mousewheel)
                self._canvas.bind_all("<Button-4>", on_mousewheel)
                self._canvas.bind_all("<Button-5>", on_mousewheel)

        def unbind_mousewheel(event):
            """Unbind global mousewheel events when mouse leaves the frame"""
            if self._canvas:
                self._canvas.unbind_all("<MouseWheel>")
                self._canvas.unbind_all("<Button-4>")
                self._canvas.unbind_all("<Button-5>")

        # Bind enter/leave events to manage global mouse wheel binding
        # Use explicit type annotation to handle mixed widget types
        widgets_to_bind: List[tk.Widget] = [self._frame]
        if self._canvas:
            widgets_to_bind.append(self._canvas)
        if self._scrollable_frame:
            widgets_to_bind.append(self._scrollable_frame)

        for widget in widgets_to_bind:
            if widget:
                widget.bind("<Enter>", bind_mousewheel)
                widget.bind("<Leave>", unbind_mousewheel)

        # Also bind directly to canvas as fallback
        if self._canvas:
            self._canvas.bind("<MouseWheel>", on_mousewheel)
            self._canvas.bind("<Button-4>", on_mousewheel)
            self._canvas.bind("<Button-5>", on_mousewheel)

            # Make canvas focusable and set focus
            self._canvas.config(takefocus=True)
            self._frame.after(
                100, lambda: self._canvas.focus_set() if self._canvas else None
            )

    def _setup_resizing(self) -> None:
        """Setup resize handling"""
        if not self._canvas:
            return

        def on_canvas_resize(event):
            # Update scrollable frame width to match canvas
            canvas_width = event.width
            if canvas_width > 1 and self._canvas:
                canvas_items = self._canvas.find_all()
                if canvas_items:
                    self._canvas.itemconfig(canvas_items[0], width=canvas_width)
                self._resize_widgets(canvas_width)

        self._canvas.bind("<Configure>", on_canvas_resize)

    def get_scrollable_container(self) -> Optional[tk.Frame]:
        """Return the container where subclasses should add their content"""
        return self._scrollable_frame

    def _resize_widgets(self, canvas_width: int) -> None:
        """Override this method in subclasses to handle widget resizing"""
        pass

    def update_scroll_region(self) -> None:
        """Update the scroll region - useful for subclasses when adding dynamic content"""
        if self._scrollable_frame and self._canvas:
            self._scrollable_frame.update_idletasks()
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def setup_frame(self) -> None:
        """Override this method in subclasses"""
        pass

    # Threading methods for non-blocking updates
    def start_threaded_updates(self, update_interval: int = 3000) -> None:
        """Start threaded updates with Windows-specific timing"""
        if self._thread_running:
            return

        # Adjust update interval for Windows
        if self._is_windows:
            update_interval = max(
                update_interval * 2, 3000
            )  # Double interval for Windows, minimum 3s

        self._stop_updates.clear()
        self._thread_running = True

        # Start the background thread
        self._update_thread = threading.Thread(
            target=self._threaded_update_loop, args=(update_interval,), daemon=True
        )
        self._update_thread.start()

        # Start processing updates on the main thread
        self._process_update_queue()

    def stop_threaded_updates(self) -> None:
        """Stop threaded updates"""
        self._stop_updates.set()
        self._thread_running = False

    def _threaded_update_loop(self, update_interval: int) -> None:
        """Background thread loop for collecting data"""
        interval_seconds = update_interval / 1000.0

        while not self._stop_updates.is_set():
            try:
                # Collect data in background thread (override in subclasses)
                data = self._collect_data_threaded()

                # Put data in queue for main thread to process
                if data is not None:
                    self._update_queue.put(data)

            except Exception as e:
                raise Exception(f"Error in threaded update: {e}")

            # Wait for next update
            self._stop_updates.wait(interval_seconds)

    def _collect_data_threaded(self) -> Optional[Any]:
        """Override this method in subclasses to collect data in background thread"""
        return None

    def _process_update_queue(self) -> None:
        """Process updates with Windows-specific batching"""
        try:
            # Process all available updates
            updates_processed = 0
            max_updates = (
                5 if self._is_windows else 10
            )  # Limit updates per cycle on Windows

            while not self._update_queue.empty() and updates_processed < max_updates:
                try:
                    data = self._update_queue.get_nowait()
                    if self._is_windows:
                        # Batch updates on Windows
                        self._batch_update_for_windows(data)
                    else:
                        self._update_ui_with_data(data)
                    updates_processed += 1
                except queue.Empty:
                    break
                except Exception as e:
                    raise Exception(f"Error processing update: {e}")

        except Exception as e:
            raise Exception(f"Error in queue processing: {e}")

        # Schedule next queue processing with Windows-specific timing
        if self._thread_running:
            delay = 1000 if self._is_windows else 500  # Slower processing on Windows
            self._frame.after(delay, self._process_update_queue)

    def _batch_update_for_windows(self, data: Any) -> None:
        """Batch UI updates for better Windows performance"""
        # Store the update data
        self._pending_updates = data

        # Cancel any existing timer
        if self._update_batch_timer:
            self._frame.after_cancel(self._update_batch_timer)

        # Schedule a batched update after a short delay
        self._update_batch_timer = self._frame.after(100, self._apply_batched_updates)

    def _apply_batched_updates(self) -> None:
        """Apply batched updates to UI"""
        if self._pending_updates:
            self._update_ui_with_data(self._pending_updates)
            self._pending_updates = {}
        self._update_batch_timer = None

    def _update_ui_with_data(self, data: Any) -> None:
        """Override this method in subclasses to update UI with collected data"""
        pass

    def __del__(self):
        """Cleanup when frame is destroyed"""
        if hasattr(self, "_stop_updates"):
            self.stop_threaded_updates()
