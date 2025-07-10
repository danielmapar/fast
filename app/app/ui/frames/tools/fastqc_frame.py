import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from typing import List, Optional, override

import psutil

from app.library.manager import LibraryManager
from app.thread.lambda_runner import LambdaThreadRunner
from app.ui.frames.base_frame import BaseFrame


class FastQCFrame(BaseFrame):
    def __init__(self, notebook: ttk.Notebook) -> None:
        self._library_manager = LibraryManager()

        # Track focusable widgets
        self._focusable_widgets: List[tk.Widget] = []

        # UI Variables
        self.input_files: List[str] = []
        self.output_dir = tk.StringVar()
        self.format_var = tk.StringVar(value="auto")
        self.threads_var = tk.StringVar(value=str(self._detect_cpu_cores()))
        self.kmers_var = tk.StringVar(value="5")
        self.extract_var = tk.BooleanVar(value=True)
        self.nogroup_var = tk.BooleanVar(value=False)
        self.casava_var = tk.BooleanVar(value=False)
        self.quiet_var = tk.BooleanVar(value=False)
        self.contaminants_file = tk.StringVar()

        # UI Elements
        self.files_listbox: Optional[tk.Listbox] = None
        self.run_button: Optional[tk.Button] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        self.status_label: Optional[tk.Label] = None

        super().__init__(notebook, "FastQC")

    @override
    def setup_frame(self) -> None:
        # Main content with padding
        main_frame = tk.Frame(self.get_scrollable_container())
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Title
        title_text = "FastQC - Quality Control Analysis"
        title_label = tk.Label(main_frame, text=title_text, font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 20))

        # Create all sections
        self._create_input_files_section(main_frame)
        self._create_output_section(main_frame)
        self._create_options_section(main_frame)
        self._create_advanced_options_section(main_frame)
        self._create_run_section(main_frame)

        # Bind focus removal to all non-input widgets
        # self._bind_focus_removal(main_frame)
        # self._bind_focus_removal(container)

    def _remove_focus(self, event=None):
        """Remove focus from any focused widget when clicking on non-input areas"""
        if not event:
            return

        clicked_widget = event.widget
        widget_class = clicked_widget.winfo_class()

        # List of widgets that should keep focus when clicked
        input_widgets = ["Entry", "Spinbox", "TCombobox", "Listbox", "Text", "Button"]

        if widget_class not in input_widgets:
            # Remove focus by setting it to the main frame
            self._frame.focus_set()
            return "break"  # Prevent event propagation

    def _bind_focus_removal(self, widget):
        """Bind focus removal to a widget and its children"""
        widget.bind("<Button-1>", self._remove_focus)

        # Recursively bind to all children
        for child in widget.winfo_children():
            child_class = child.winfo_class()
            # Don't bind to input widgets as they need to maintain focus
            if child_class not in [
                "Entry",
                "Spinbox",
                "TCombobox",
                "Listbox",
                "Text",
                "Button",
                "Checkbutton",  # Add Checkbutton to exclusion list
            ]:
                self._bind_focus_removal(child)

    def _detect_cpu_cores(self) -> int:
        """Detect the number of available CPU cores"""
        try:
            # Use psutil for more accurate detection
            logical_cores = psutil.cpu_count(logical=True)
            if logical_cores:
                return logical_cores
        except Exception:
            pass

        # Fallback to os.cpu_count()
        cores = os.cpu_count()
        if cores:
            return cores

        # Ultimate fallback
        return 2

    def _create_input_files_section(self, parent: tk.Widget) -> None:
        """Create the input files selection section"""
        files_frame = tk.LabelFrame(parent, text="Input Files", padx=15, pady=10)
        files_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Instructions
        instructions = tk.Label(
            files_frame,
            text="Select FASTQ, SAM, or BAM files for quality control analysis",
            font=("Arial", 9),
            fg="gray",
        )
        instructions.pack(anchor="w", pady=(0, 10))

        # File selection buttons
        button_frame = tk.Frame(files_frame)
        button_frame.pack(fill="x", pady=(0, 10))

        tk.Button(
            button_frame,
            text="+ Add Files",
            command=self._add_files,
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5,
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            button_frame,
            text="+ Add Directory",
            command=self._add_directory,
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=5,
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            button_frame,
            text="✖ Clear",
            command=self._clear_files,
            bg="#f44336",
            fg="white",
            padx=20,
            pady=5,
        ).pack(side="left")

        # Files list with scrollbar
        list_frame = tk.Frame(files_frame)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        scrollbar_files = tk.Scrollbar(list_frame, orient="vertical")
        scrollbar_files.pack(side="right", fill="y")

        self.files_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar_files.set,
            height=6,
            selectmode=tk.SINGLE,
        )
        self.files_listbox.pack(side="left", fill="both", expand=True)
        scrollbar_files.config(command=self.files_listbox.yview)

        # Remove selected file button
        tk.Button(
            files_frame,
            text="✖ Remove Selected",
            command=self._remove_selected_file,
            padx=20,
            pady=5,
        ).pack()

    def _create_output_section(self, parent: tk.Widget) -> None:
        """Create the output directory selection section"""
        output_frame = tk.LabelFrame(parent, text="Output Directory", padx=15, pady=10)
        output_frame.pack(fill="x", pady=(0, 15))

        dir_frame = tk.Frame(output_frame)
        dir_frame.pack(fill="x")

        tk.Label(dir_frame, text="Output Directory:", width=15, anchor="w").pack(
            side="left"
        )

        # Pack the Browse button FIRST to reserve its space
        tk.Button(
            dir_frame, text="Browse", command=self._browse_output_dir, padx=15
        ).pack(side="right")

        # Then pack the Entry to fill remaining space
        tk.Entry(dir_frame, textvariable=self.output_dir).pack(
            side="left", padx=(10, 10), fill="x", expand=True
        )

    def _create_options_section(self, parent: tk.Widget) -> None:
        """Create the basic options section"""
        options_frame = tk.LabelFrame(parent, text="Basic Options", padx=15, pady=10)
        options_frame.pack(fill="x", pady=(0, 15))

        # Format selection row
        format_frame = tk.Frame(options_frame)
        format_frame.pack(fill="x", pady=(0, 10))

        tk.Label(format_frame, text="File Format:", width=15, anchor="w").pack(
            side="left"
        )
        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.format_var,
            width=20,
            values=["auto", "fastq", "bam", "sam", "bam_mapped", "sam_mapped"],
            state="readonly",
        )
        format_combo.pack(side="left", padx=(10, 0))

        # Disable mouse wheel scrolling on format combobox
        format_combo.bind("<MouseWheel>", lambda e: "break")
        format_combo.bind("<Button-4>", lambda e: "break")  # Linux scroll up
        format_combo.bind("<Button-5>", lambda e: "break")  # Linux scroll down

        # Threads selection row
        threads_frame = tk.Frame(options_frame)
        threads_frame.pack(fill="x", pady=(0, 10))

        tk.Label(threads_frame, text="Threads:", width=15, anchor="w").pack(side="left")
        tk.Spinbox(
            threads_frame, from_=1, to=8, textvariable=self.threads_var, width=10
        ).pack(side="left", padx=(10, 0))

        # Extract option
        tk.Checkbutton(
            options_frame,
            text="Extract zip files after creation",
            variable=self.extract_var,
        ).pack(anchor="w")

    def _create_advanced_options_section(self, parent: tk.Widget) -> None:
        """Create the advanced options section"""
        advanced_frame = tk.LabelFrame(
            parent, text="Advanced Options", padx=15, pady=10
        )
        advanced_frame.pack(fill="x", pady=(0, 15))

        # K-mers length row
        kmers_frame = tk.Frame(advanced_frame)
        kmers_frame.pack(fill="x", pady=(0, 10))

        tk.Label(kmers_frame, text="K-mer Length:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Spinbox(
            kmers_frame, from_=2, to=10, textvariable=self.kmers_var, width=10
        ).pack(side="left", padx=(10, 0))

        # Contaminants file row
        contam_frame = tk.Frame(advanced_frame)
        contam_frame.pack(fill="x", pady=(0, 10))

        tk.Label(contam_frame, text="Contaminants File:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(contam_frame, textvariable=self.contaminants_file).pack(
            side="left", padx=(10, 10), fill="x", expand=True
        )
        tk.Button(
            contam_frame, text="Browse", command=self._browse_contaminants_file, padx=15
        ).pack(side="right")

        # Boolean options in a grid
        options_grid = tk.Frame(advanced_frame)
        options_grid.pack(fill="x")

        tk.Checkbutton(
            options_grid, text="No grouping (--nogroup)", variable=self.nogroup_var
        ).grid(row=0, column=0, sticky="w", padx=(0, 30))

        tk.Checkbutton(
            options_grid, text="Casava mode (--casava)", variable=self.casava_var
        ).grid(row=0, column=1, sticky="w", padx=(0, 30))

        tk.Checkbutton(
            options_grid, text="Quiet mode (--quiet)", variable=self.quiet_var
        ).grid(row=1, column=0, sticky="w", columnspan=2)

    def _create_run_section(self, parent: tk.Widget) -> None:
        """Create the run section with status and progress"""
        run_frame = tk.Frame(parent)
        run_frame.pack(fill="x", pady=(15, 0))

        # Status label
        self.status_label = tk.Label(
            run_frame,
            text="Ready to run FastQC analysis",
            font=("Arial", 10),
            fg="green",
        )
        self.status_label.pack(pady=(0, 10))

        # Progress bar
        self.progress_bar = ttk.Progressbar(run_frame, mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=(0, 15))

        # Run button
        self.run_button = tk.Button(
            run_frame,
            text="▶ Run FastQC Analysis",
            command=self._run_fastqc,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            pady=15,
        )
        self.run_button.pack(fill="x")

    def _add_files(self) -> None:
        """Add individual files to the input list"""
        files = filedialog.askopenfilenames(
            title="Select sequence files",
            filetypes=[
                ("All supported", "*.fastq *.fq *.fastq.gz *.fq.gz *.bam *.sam"),
                ("FASTQ files", "*.fastq *.fq *.fastq.gz *.fq.gz"),
                ("BAM files", "*.bam"),
                ("SAM files", "*.sam"),
                ("All files", "*.*"),
            ],
        )

        for file in files:
            if file not in self.input_files:
                self.input_files.append(file)
                if self.files_listbox:
                    self.files_listbox.insert(tk.END, os.path.basename(file))

        self._update_status()

    def _add_directory(self) -> None:
        """Add all supported files from a directory"""
        directory = filedialog.askdirectory(
            title="Select directory containing sequence files"
        )
        if not directory:
            return

        supported_extensions = (".fastq", ".fq", ".fastq.gz", ".fq.gz", ".bam", ".sam")
        added_count = 0

        for filename in os.listdir(directory):
            if filename.lower().endswith(supported_extensions):
                filepath = os.path.join(directory, filename)
                if filepath not in self.input_files:
                    self.input_files.append(filepath)
                    if self.files_listbox:
                        self.files_listbox.insert(tk.END, filename)
                    added_count += 1

        if added_count > 0:
            messagebox.showinfo(
                "Files Added", f"Added {added_count} files from directory"
            )
        else:
            messagebox.showwarning(
                "No Files", "No supported sequence files found in directory"
            )

        self._update_status()

    def _clear_files(self) -> None:
        """Clear all input files"""
        self.input_files.clear()
        if self.files_listbox:
            self.files_listbox.delete(0, tk.END)
        self._update_status()

    def _remove_selected_file(self) -> None:
        """Remove the selected file from the list"""
        if not self.files_listbox:
            return

        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            self.input_files.pop(index)
            self.files_listbox.delete(index)
            self._update_status()

    def _browse_output_dir(self) -> None:
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_dir.set(directory)

    def _browse_contaminants_file(self) -> None:
        """Browse for contaminants file"""
        file = filedialog.askopenfilename(
            title="Select contaminants file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file:
            self.contaminants_file.set(file)

    def _update_status(self) -> None:
        """Update the status label based on current state"""
        if not self.status_label:
            return

        file_count = len(self.input_files)
        if file_count == 0:
            self.status_label.config(text="No files selected", fg="gray")
        else:
            self.status_label.config(
                text=f"Ready to analyze {file_count} file(s)", fg="green"
            )

    def _build_fastqc_command(self) -> List[str]:
        """Build FastQC command based on current UI settings"""
        if not self.input_files:
            raise ValueError("No input files selected")

        command = []

        # Output directory
        if self.output_dir.get():
            command.extend(["-o", self.output_dir.get()])

        # Format
        if self.format_var.get() != "auto":
            command.extend(["-f", self.format_var.get()])

        # Threads
        threads = int(self.threads_var.get())
        if threads > 1:
            command.extend(["-t", str(threads)])

        # Extract option
        if not self.extract_var.get():
            print("No extract")
            command.append("--noextract")

        # K-mers
        kmers = int(self.kmers_var.get())
        if kmers != 5:
            command.extend(["-k", str(kmers)])

        # Contaminants file
        if self.contaminants_file.get():
            command.extend(["-c", self.contaminants_file.get()])

        # Boolean options
        if self.nogroup_var.get():
            command.append("--nogroup")

        if self.casava_var.get():
            command.append("--casava")

        if self.quiet_var.get():
            command.append("--quiet")

        # Add input files
        command.extend(self.input_files)

        return command

    def _run_fastqc(self) -> None:
        """Run FastQC analysis"""
        try:
            # Validate inputs
            if not self.input_files:
                messagebox.showerror("Error", "Please select at least one input file")
                return

            # Check if output directory exists, create if needed
            output_dir = self.output_dir.get()
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Could not create output directory: {e}"
                    )
                    return

            # Build command
            command = self._build_fastqc_command()

            # Update UI for running state
            self._set_running_state(True)

            # Run FastQC in background thread
            thread = LambdaThreadRunner(
                target_function=lambda: self._library_manager.run_fastqc_command(
                    command
                ),
                on_success=lambda result: self._on_fastqc_complete(True, None),
                on_error=lambda error: self._on_fastqc_complete(False, error),
            )
            thread.start()

        except Exception as e:
            self._on_fastqc_complete(False, e)

    def _set_running_state(self, running: bool) -> None:
        """Set UI state for running/not running"""
        if self.run_button:
            self.run_button.config(state="disabled" if running else "normal")

        if self.status_label:
            if running:
                self.status_label.config(text="Running FastQC analysis...", fg="orange")
            else:
                self._update_status()

        if self.progress_bar:
            if running:
                self.progress_bar.start()
            else:
                self.progress_bar.stop()

    def _on_fastqc_complete(self, success: bool, error: Optional[Exception]) -> None:
        """Handle FastQC completion"""
        self._set_running_state(False)

        if success:
            if self.status_label:
                self.status_label.config(
                    text="FastQC analysis completed successfully!", fg="green"
                )
            messagebox.showinfo("Success", "FastQC analysis completed successfully!")
        else:
            if self.status_label:
                self.status_label.config(text="FastQC analysis failed", fg="red")
            error_msg = (
                f"FastQC analysis failed: {str(error)}"
                if error
                else "FastQC analysis failed"
            )
            messagebox.showerror("Error", error_msg)
