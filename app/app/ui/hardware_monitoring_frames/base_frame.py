import platform
import tkinter as tk
import tkinter.ttk as ttk
from typing import List, Optional


class BaseHardwareMonitoringFrame:
    def __init__(self, notebook: ttk.Notebook, tab_name: str) -> None:
        self._notebook = notebook
        self._frame = ttk.Frame(self._notebook)
        self._notebook.add(self._frame, text=tab_name)

        # Initialize scrollable frame components
        self._canvas: Optional[tk.Canvas] = None
        self._scrollbar: Optional[ttk.Scrollbar] = None
        self._scrollable_frame: Optional[tk.Frame] = None

        self._setup_scrollable_frame()
        self.setup_frame()

    def _setup_scrollable_frame(self) -> None:
        """Setup scrollable canvas and frame"""
        # Create canvas and scrollbar
        self._canvas = tk.Canvas(self._frame, highlightthickness=0)
        self._scrollbar = ttk.Scrollbar(
            self._frame, orient="vertical", command=self._canvas.yview
        )
        self._scrollable_frame = tk.Frame(self._canvas)

        # Configure scrolling
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
