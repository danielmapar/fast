import os
import time
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from typing import List, Optional, override

import psutil

from app.library.manager import LibraryManager
from app.logger.config import Logger, LogType
from app.thread.lambda_runner import LambdaThreadRunner
from app.ui.frames.base_frame import BaseFrame
from app.ui.widgets.log_file_monitor import LogFileMonitor


class FastPFrame(BaseFrame):
    def __init__(self, notebook: ttk.Notebook) -> None:
        self._library_manager = LibraryManager()
        self._fastp_log_file = Logger().get_log_file_path(LogType.FASTP)

        # UI Variables
        self.input_files: List[str] = []
        self.output_dir = tk.StringVar()
        self.threads_var = tk.StringVar(value=str(self._detect_cpu_cores()))
        self.compression_var = tk.StringVar(value="4")
        self.length_required_var = tk.StringVar(value="15")
        self.length_limit_var = tk.StringVar(value="0")

        # Quality filtering options
        self.qualified_quality_var = tk.StringVar(value="30")
        self.unqualified_percent_var = tk.StringVar(value="40")
        self.n_base_limit_var = tk.StringVar(value="5")
        self.average_qual_var = tk.StringVar(value="0")

        # Trimming options
        self.trim_front1_var = tk.StringVar(value="0")
        self.trim_tail1_var = tk.StringVar(value="0")
        self.trim_front2_var = tk.StringVar(value="0")
        self.trim_tail2_var = tk.StringVar(value="0")
        self.max_len1_var = tk.StringVar(value="0")
        self.max_len2_var = tk.StringVar(value="0")

        # Adapter options
        self.disable_adapter_trimming_var = tk.BooleanVar(value=False)
        self.adapter_sequence_var = tk.StringVar()
        self.adapter_sequence_r2_var = tk.StringVar()
        self.detect_adapter_for_pe_var = tk.BooleanVar(value=False)

        # Quality cutting options
        self.cut_front_var = tk.BooleanVar(value=False)
        self.cut_tail_var = tk.BooleanVar(value=False)
        self.cut_right_var = tk.BooleanVar(value=False)
        self.cut_window_size_var = tk.StringVar(value="4")
        self.cut_mean_quality_var = tk.StringVar(value="20")

        # PolyG/PolyX trimming
        self.trim_poly_g_var = tk.BooleanVar(value=True)
        self.poly_g_min_len_var = tk.StringVar(value="10")
        self.trim_poly_x_var = tk.BooleanVar(value=False)
        self.poly_x_min_len_var = tk.StringVar(value="10")

        # Other options
        self.disable_quality_filtering_var = tk.BooleanVar(value=False)
        self.disable_length_filtering_var = tk.BooleanVar(value=False)
        self.low_complexity_filter_var = tk.BooleanVar(value=False)
        self.complexity_threshold_var = tk.StringVar(value="30")
        self.dedup_var = tk.BooleanVar(value=False)
        self.correction_var = tk.BooleanVar(value=False)
        self.merge_var = tk.BooleanVar(value=False)

        # Output files
        self.merged_out_var = tk.StringVar()
        self.failed_out_var = tk.StringVar()

        # Additional I/O options
        self.unpaired1_var = tk.StringVar()
        self.unpaired2_var = tk.StringVar()
        self.overlapped_out_var = tk.StringVar()
        self.include_unmerged_var = tk.BooleanVar(value=False)
        self.phred64_var = tk.BooleanVar(value=False)
        self.reads_to_process_var = tk.StringVar(value="0")
        self.dont_overwrite_var = tk.BooleanVar(value=False)
        self.fix_mgi_id_var = tk.BooleanVar(value=False)

        # Advanced adapter options
        self.adapter_fasta_var = tk.StringVar()
        self.allow_gap_overlap_var = tk.BooleanVar(value=False)

        # UMI options
        self.umi_var = tk.BooleanVar(value=False)
        self.umi_loc_var = tk.StringVar(value="")
        self.umi_len_var = tk.StringVar(value="0")
        self.umi_prefix_var = tk.StringVar()
        self.umi_skip_var = tk.StringVar(value="0")

        # Base correction detailed options
        self.overlap_len_require_var = tk.StringVar(value="30")
        self.overlap_diff_limit_var = tk.StringVar(value="5")
        self.overlap_diff_percent_limit_var = tk.StringVar(value="20")

        # Overrepresentation analysis
        self.overrepresentation_analysis_var = tk.BooleanVar(value=False)
        self.overrepresentation_sampling_var = tk.StringVar(value="20")

        # Report options
        self.report_title_var = tk.StringVar(value="fastp report")

        # Deduplication options
        self.dup_calc_accuracy_var = tk.StringVar(value="1")
        self.dont_eval_duplication_var = tk.BooleanVar(value=False)

        # Output splitting
        self.split_var = tk.StringVar(value="0")
        self.split_by_lines_var = tk.StringVar(value="0")
        self.split_prefix_digits_var = tk.StringVar(value="4")

        # Add missing variables after the existing ones:

        # Additional I/O and processing options
        self.verbose_var = tk.BooleanVar(value=False)
        self.interleaved_in_var = tk.BooleanVar(value=False)

        # UMI delimiter (missing from existing UMI options)
        self.umi_delim_var = tk.StringVar(value=":")

        # Advanced quality cutting options
        self.cut_front_window_size_var = tk.StringVar(value="4")
        self.cut_front_mean_quality_var = tk.StringVar(value="20")
        self.cut_tail_window_size_var = tk.StringVar(value="4")
        self.cut_tail_mean_quality_var = tk.StringVar(value="20")
        self.cut_right_window_size_var = tk.StringVar(value="4")
        self.cut_right_mean_quality_var = tk.StringVar(value="20")

        # Index filtering options
        self.filter_by_index1_var = tk.StringVar()
        self.filter_by_index2_var = tk.StringVar()
        self.filter_by_index_threshold_var = tk.StringVar(value="0")

        # Timing variable
        self.start_time: Optional[float] = None

        # UI Elements
        self.files_listbox: Optional[tk.Listbox] = None
        self.run_button: Optional[tk.Button] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        self.status_label: Optional[tk.Label] = None

        super().__init__(notebook, "FastP")

    @override
    def setup_frame(self) -> None:
        # Main content with padding
        self.main_frame = tk.Frame(self.get_scrollable_container())
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Title
        title_text = "FastP - Ultra-fast FASTQ Preprocessor"
        title_label = tk.Label(
            self.main_frame, text=title_text, font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Create all sections
        self._create_input_files_section()
        self._create_output_section()
        self._create_basic_options_section()
        self._create_quality_filtering_section()
        self._create_trimming_section()
        self._create_adapter_section()
        self._create_quality_cutting_section()
        self._create_polyg_polyx_section()
        self._create_advanced_options_section()
        self._create_umi_section()
        self._create_overlap_correction_section()
        self._create_overrepresentation_section()
        self._create_deduplication_section()
        self._create_output_splitting_section()
        self._create_report_options_section()
        self._create_additional_io_section()
        self._create_index_filtering_section()
        self._create_run_section()

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
        return 1

    def _create_input_files_section(self) -> None:
        """Create the input files selection section"""
        files_frame = tk.LabelFrame(
            self.main_frame, text="Input Files", padx=15, pady=10
        )
        files_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Instructions
        instructions = tk.Label(
            files_frame,
            text="Select FASTQ files for preprocessing and quality control",
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

    def _create_output_section(self) -> None:
        """Create the output directory selection section"""
        output_frame = tk.LabelFrame(
            self.main_frame, text="Output Options", padx=15, pady=10
        )
        output_frame.pack(fill="x", pady=(0, 15))

        # Output directory
        dir_frame = tk.Frame(output_frame)
        dir_frame.pack(fill="x", pady=(0, 10))

        tk.Label(dir_frame, text="Output Directory:", width=15, anchor="w").pack(
            side="left"
        )

        tk.Button(
            dir_frame, text="Browse", command=self._browse_output_dir, padx=15
        ).pack(side="right")

        tk.Entry(dir_frame, textvariable=self.output_dir).pack(
            side="left", padx=(10, 10), fill="x", expand=True
        )

        # Additional output files
        # Merged output
        merged_frame = tk.Frame(output_frame)
        merged_frame.pack(fill="x", pady=(0, 5))

        tk.Label(merged_frame, text="Merged Output:", width=15, anchor="w").pack(
            side="left"
        )

        tk.Button(
            merged_frame, text="Browse", command=self._browse_merged_out, padx=15
        ).pack(side="right")

        tk.Entry(merged_frame, textvariable=self.merged_out_var).pack(
            side="left", padx=(10, 10), fill="x", expand=True
        )

        # Failed output
        failed_frame = tk.Frame(output_frame)
        failed_frame.pack(fill="x", pady=(0, 5))

        tk.Label(failed_frame, text="Failed Reads:", width=15, anchor="w").pack(
            side="left"
        )

        tk.Button(
            failed_frame, text="Browse", command=self._browse_failed_out, padx=15
        ).pack(side="right")

        tk.Entry(failed_frame, textvariable=self.failed_out_var).pack(
            side="left", padx=(10, 10), fill="x", expand=True
        )

    def _create_basic_options_section(self) -> None:
        """Create the basic options section"""
        options_frame = tk.LabelFrame(
            self.main_frame, text="Basic Options", padx=15, pady=10
        )
        options_frame.pack(fill="x", pady=(0, 15))

        # Threads and compression in first row
        row1_frame = tk.Frame(options_frame)
        row1_frame.pack(fill="x", pady=(0, 10))

        tk.Label(row1_frame, text="Threads:", width=15, anchor="w").pack(side="left")
        tk.Spinbox(
            row1_frame, from_=1, to=16, textvariable=self.threads_var, width=10
        ).pack(side="left", padx=(10, 20))

        tk.Label(row1_frame, text="Compression (1-9):", width=15, anchor="w").pack(
            side="left"
        )
        tk.Spinbox(
            row1_frame, from_=1, to=9, textvariable=self.compression_var, width=10
        ).pack(side="left", padx=(10, 0))

        # Length filtering in second row
        row2_frame = tk.Frame(options_frame)
        row2_frame.pack(fill="x", pady=(0, 10))

        tk.Label(row2_frame, text="Min Length:", width=15, anchor="w").pack(side="left")
        tk.Entry(row2_frame, textvariable=self.length_required_var, width=10).pack(
            side="left", padx=(10, 20)
        )

        tk.Label(row2_frame, text="Max Length:", width=15, anchor="w").pack(side="left")
        tk.Entry(row2_frame, textvariable=self.length_limit_var, width=10).pack(
            side="left", padx=(10, 0)
        )

        # Boolean options
        tk.Checkbutton(
            options_frame, text="Merge paired-end reads", variable=self.merge_var
        ).pack(anchor="w")

        tk.Checkbutton(
            options_frame, text="Enable deduplication", variable=self.dedup_var
        ).pack(anchor="w")

        tk.Checkbutton(
            options_frame, text="Enable base correction", variable=self.correction_var
        ).pack(anchor="w")

    def _create_quality_filtering_section(self) -> None:
        """Create the quality filtering section"""
        quality_frame = tk.LabelFrame(
            self.main_frame, text="Quality Filtering", padx=15, pady=10
        )
        quality_frame.pack(fill="x", pady=(0, 15))

        # Disable quality filtering checkbox
        tk.Checkbutton(
            quality_frame,
            text="Disable quality filtering",
            variable=self.disable_quality_filtering_var,
        ).pack(anchor="w", pady=(0, 10))

        # Quality parameters
        row1_frame = tk.Frame(quality_frame)
        row1_frame.pack(fill="x", pady=(0, 10))

        tk.Label(row1_frame, text="Qualified Quality:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(row1_frame, textvariable=self.qualified_quality_var, width=10).pack(
            side="left", padx=(10, 20)
        )

        tk.Label(row1_frame, text="Unqualified %:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(row1_frame, textvariable=self.unqualified_percent_var, width=10).pack(
            side="left", padx=(10, 0)
        )

        row2_frame = tk.Frame(quality_frame)
        row2_frame.pack(fill="x")

        tk.Label(row2_frame, text="N Base Limit:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(row2_frame, textvariable=self.n_base_limit_var, width=10).pack(
            side="left", padx=(10, 20)
        )

        tk.Label(row2_frame, text="Average Quality:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(row2_frame, textvariable=self.average_qual_var, width=10).pack(
            side="left", padx=(10, 0)
        )

    def _create_trimming_section(self) -> None:
        """Create the global trimming section"""
        trimming_frame = tk.LabelFrame(
            self.main_frame, text="Global Trimming", padx=15, pady=10
        )
        trimming_frame.pack(fill="x", pady=(0, 15))

        # Read 1 trimming
        read1_frame = tk.Frame(trimming_frame)
        read1_frame.pack(fill="x", pady=(0, 10))

        tk.Label(read1_frame, text="Read1 Front:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(read1_frame, textvariable=self.trim_front1_var, width=10).pack(
            side="left", padx=(10, 20)
        )

        tk.Label(read1_frame, text="Read1 Tail:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(read1_frame, textvariable=self.trim_tail1_var, width=10).pack(
            side="left", padx=(10, 20)
        )

        tk.Label(read1_frame, text="Read1 Max Len:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(read1_frame, textvariable=self.max_len1_var, width=10).pack(
            side="left", padx=(10, 0)
        )

        # Read 2 trimming
        read2_frame = tk.Frame(trimming_frame)
        read2_frame.pack(fill="x")

        tk.Label(read2_frame, text="Read2 Front:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(read2_frame, textvariable=self.trim_front2_var, width=10).pack(
            side="left", padx=(10, 20)
        )

        tk.Label(read2_frame, text="Read2 Tail:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(read2_frame, textvariable=self.trim_tail2_var, width=10).pack(
            side="left", padx=(10, 20)
        )

        tk.Label(read2_frame, text="Read2 Max Len:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(read2_frame, textvariable=self.max_len2_var, width=10).pack(
            side="left", padx=(10, 0)
        )

    def _create_adapter_section(self) -> None:
        """Create the adapter trimming section"""
        adapter_frame = tk.LabelFrame(
            self.main_frame, text="Adapter Trimming", padx=15, pady=10
        )
        adapter_frame.pack(fill="x", pady=(0, 15))

        # Disable adapter trimming
        tk.Checkbutton(
            adapter_frame,
            text="Disable adapter trimming",
            variable=self.disable_adapter_trimming_var,
        ).pack(anchor="w", pady=(0, 10))

        # Adapter sequences
        adapter1_frame = tk.Frame(adapter_frame)
        adapter1_frame.pack(fill="x", pady=(0, 5))

        tk.Label(adapter1_frame, text="Adapter R1:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(adapter1_frame, textvariable=self.adapter_sequence_var).pack(
            side="left", padx=(10, 10), fill="x", expand=True
        )

        adapter2_frame = tk.Frame(adapter_frame)
        adapter2_frame.pack(fill="x", pady=(0, 10))

        tk.Label(adapter2_frame, text="Adapter R2:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(adapter2_frame, textvariable=self.adapter_sequence_r2_var).pack(
            side="left", padx=(10, 10), fill="x", expand=True
        )

        # Detect adapter for PE
        tk.Checkbutton(
            adapter_frame,
            text="Detect adapter for paired-end data",
            variable=self.detect_adapter_for_pe_var,
        ).pack(anchor="w")

    def _create_quality_cutting_section(self) -> None:
        """Create the quality cutting section"""
        cutting_frame = tk.LabelFrame(
            self.main_frame, text="Quality Cutting", padx=15, pady=10
        )
        cutting_frame.pack(fill="x", pady=(0, 15))

        # Cutting options
        options_frame = tk.Frame(cutting_frame)
        options_frame.pack(fill="x", pady=(0, 10))

        tk.Checkbutton(
            options_frame, text="Cut front (5')", variable=self.cut_front_var
        ).pack(side="left", padx=(0, 20))

        tk.Checkbutton(
            options_frame, text="Cut tail (3')", variable=self.cut_tail_var
        ).pack(side="left", padx=(0, 20))

        tk.Checkbutton(
            options_frame, text="Cut right", variable=self.cut_right_var
        ).pack(side="left")

        # Global parameters (used as default for all cutting types)
        global_params_frame = tk.Frame(cutting_frame)
        global_params_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            global_params_frame, text="Global Window Size:", width=18, anchor="w"
        ).pack(side="left")
        tk.Entry(
            global_params_frame, textvariable=self.cut_window_size_var, width=8
        ).pack(side="left", padx=(10, 20))

        tk.Label(
            global_params_frame, text="Global Mean Quality:", width=18, anchor="w"
        ).pack(side="left")
        tk.Entry(
            global_params_frame, textvariable=self.cut_mean_quality_var, width=8
        ).pack(side="left", padx=(10, 0))

        # Advanced cutting parameters
        advanced_label = tk.Label(
            cutting_frame,
            text="Advanced Parameters (override global settings when specified):",
            font=("Arial", 9, "bold"),
        )
        advanced_label.pack(anchor="w", pady=(10, 5))

        # Front cutting parameters
        front_params_frame = tk.Frame(cutting_frame)
        front_params_frame.pack(fill="x", pady=(0, 5))

        tk.Label(
            front_params_frame, text="Front Window Size:", width=18, anchor="w"
        ).pack(side="left")
        tk.Entry(
            front_params_frame, textvariable=self.cut_front_window_size_var, width=8
        ).pack(side="left", padx=(10, 20))

        tk.Label(
            front_params_frame, text="Front Mean Quality:", width=18, anchor="w"
        ).pack(side="left")
        tk.Entry(
            front_params_frame, textvariable=self.cut_front_mean_quality_var, width=8
        ).pack(side="left", padx=(10, 0))

        # Tail cutting parameters
        tail_params_frame = tk.Frame(cutting_frame)
        tail_params_frame.pack(fill="x", pady=(0, 5))

        tk.Label(
            tail_params_frame, text="Tail Window Size:", width=18, anchor="w"
        ).pack(side="left")
        tk.Entry(
            tail_params_frame, textvariable=self.cut_tail_window_size_var, width=8
        ).pack(side="left", padx=(10, 20))

        tk.Label(
            tail_params_frame, text="Tail Mean Quality:", width=18, anchor="w"
        ).pack(side="left")
        tk.Entry(
            tail_params_frame, textvariable=self.cut_tail_mean_quality_var, width=8
        ).pack(side="left", padx=(10, 0))

        # Right cutting parameters
        right_params_frame = tk.Frame(cutting_frame)
        right_params_frame.pack(fill="x")

        tk.Label(
            right_params_frame, text="Right Window Size:", width=18, anchor="w"
        ).pack(side="left")
        tk.Entry(
            right_params_frame, textvariable=self.cut_right_window_size_var, width=8
        ).pack(side="left", padx=(10, 20))

        tk.Label(
            right_params_frame, text="Right Mean Quality:", width=18, anchor="w"
        ).pack(side="left")
        tk.Entry(
            right_params_frame, textvariable=self.cut_right_mean_quality_var, width=8
        ).pack(side="left", padx=(10, 0))

        # Help text
        help_text = tk.Label(
            cutting_frame,
            text=(
                "Note: Advanced parameters override global settings for specific "
                "operations. Leave blank to use global values."
            ),
            font=("Arial", 8),
            fg="gray",
            wraplength=600,
        )
        help_text.pack(anchor="w", pady=(10, 0))

    def _create_polyg_polyx_section(self) -> None:
        """Create the polyG/PolyX trimming section"""
        poly_frame = tk.LabelFrame(
            self.main_frame, text="PolyG/PolyX Trimming", padx=15, pady=10
        )
        poly_frame.pack(fill="x", pady=(0, 15))

        # PolyG options
        polyg_frame = tk.Frame(poly_frame)
        polyg_frame.pack(fill="x", pady=(0, 10))

        tk.Checkbutton(
            polyg_frame, text="Trim polyG", variable=self.trim_poly_g_var
        ).pack(side="left", padx=(0, 20))

        tk.Label(polyg_frame, text="PolyG Min Len:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(polyg_frame, textvariable=self.poly_g_min_len_var, width=10).pack(
            side="left", padx=(10, 0)
        )

        # PolyX options
        polyx_frame = tk.Frame(poly_frame)
        polyx_frame.pack(fill="x")

        tk.Checkbutton(
            polyx_frame, text="Trim polyX", variable=self.trim_poly_x_var
        ).pack(side="left", padx=(0, 20))

        tk.Label(polyx_frame, text="PolyX Min Len:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(polyx_frame, textvariable=self.poly_x_min_len_var, width=10).pack(
            side="left", padx=(10, 0)
        )

    def _create_advanced_options_section(self) -> None:
        """Create the advanced options section"""
        advanced_frame = tk.LabelFrame(
            self.main_frame, text="Advanced Options", padx=15, pady=10
        )
        advanced_frame.pack(fill="x", pady=(0, 15))

        # Length filtering disable
        tk.Checkbutton(
            advanced_frame,
            text="Disable length filtering",
            variable=self.disable_length_filtering_var,
        ).pack(anchor="w", pady=(0, 10))

        # Low complexity filter
        complexity_frame = tk.Frame(advanced_frame)
        complexity_frame.pack(fill="x")

        tk.Checkbutton(
            complexity_frame,
            text="Low complexity filter",
            variable=self.low_complexity_filter_var,
        ).pack(side="left", padx=(0, 20))

        tk.Label(
            complexity_frame, text="Complexity Threshold:", width=18, anchor="w"
        ).pack(side="left")
        tk.Entry(
            complexity_frame, textvariable=self.complexity_threshold_var, width=10
        ).pack(side="left", padx=(10, 0))

    def _create_umi_section(self) -> None:
        """Create the UMI processing section"""
        umi_frame = tk.LabelFrame(
            self.main_frame, text="UMI Processing", padx=15, pady=10
        )
        umi_frame.pack(fill="x", pady=(0, 15))

        # Enable UMI
        tk.Checkbutton(
            umi_frame, text="Enable UMI preprocessing", variable=self.umi_var
        ).pack(anchor="w", pady=(0, 10))

        # UMI location
        umi_loc_frame = tk.Frame(umi_frame)
        umi_loc_frame.pack(fill="x", pady=(0, 10))

        tk.Label(umi_loc_frame, text="UMI Location:", width=15, anchor="w").pack(
            side="left"
        )
        umi_loc_combo = ttk.Combobox(
            umi_loc_frame,
            textvariable=self.umi_loc_var,
            width=20,
            values=["", "index1", "index2", "read1", "read2", "per_index", "per_read"],
            state="readonly",
        )
        umi_loc_combo.pack(side="left", padx=(10, 20))

        tk.Label(umi_loc_frame, text="UMI Length:", width=12, anchor="w").pack(
            side="left"
        )
        tk.Entry(umi_loc_frame, textvariable=self.umi_len_var, width=10).pack(
            side="left", padx=(10, 0)
        )

        # UMI prefix and skip
        umi_params_frame = tk.Frame(umi_frame)
        umi_params_frame.pack(fill="x", pady=(0, 10))

        tk.Label(umi_params_frame, text="UMI Prefix:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(umi_params_frame, textvariable=self.umi_prefix_var, width=15).pack(
            side="left", padx=(10, 20)
        )

        tk.Label(umi_params_frame, text="UMI Skip:", width=12, anchor="w").pack(
            side="left"
        )
        tk.Entry(umi_params_frame, textvariable=self.umi_skip_var, width=10).pack(
            side="left", padx=(10, 0)
        )

        # ADD UMI delimiter option
        umi_delim_frame = tk.Frame(umi_frame)
        umi_delim_frame.pack(fill="x")

        tk.Label(umi_delim_frame, text="UMI Delimiter:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(umi_delim_frame, textvariable=self.umi_delim_var, width=10).pack(
            side="left", padx=(10, 20)
        )
        tk.Label(
            umi_delim_frame, text="(default: :)", font=("Arial", 9), fg="gray"
        ).pack(side="left")

    def _create_overlap_correction_section(self) -> None:
        """Create the overlap correction section"""
        overlap_frame = tk.LabelFrame(
            self.main_frame, text="Overlap Correction Settings", padx=15, pady=10
        )
        overlap_frame.pack(fill="x", pady=(0, 15))

        # Overlap parameters
        overlap_params_frame = tk.Frame(overlap_frame)
        overlap_params_frame.pack(fill="x")

        tk.Label(
            overlap_params_frame, text="Min Overlap Len:", width=15, anchor="w"
        ).pack(side="left")
        tk.Entry(
            overlap_params_frame, textvariable=self.overlap_len_require_var, width=10
        ).pack(side="left", padx=(10, 20))

        tk.Label(overlap_params_frame, text="Max Diff:", width=12, anchor="w").pack(
            side="left"
        )
        tk.Entry(
            overlap_params_frame, textvariable=self.overlap_diff_limit_var, width=10
        ).pack(side="left", padx=(10, 20))

        tk.Label(overlap_params_frame, text="Max Diff %:", width=12, anchor="w").pack(
            side="left"
        )
        tk.Entry(
            overlap_params_frame,
            textvariable=self.overlap_diff_percent_limit_var,
            width=10,
        ).pack(side="left", padx=(10, 0))

    def _create_overrepresentation_section(self) -> None:
        """Create the overrepresentation analysis section"""
        overrep_frame = tk.LabelFrame(
            self.main_frame, text="Overrepresentation Analysis", padx=15, pady=10
        )
        overrep_frame.pack(fill="x", pady=(0, 15))

        # Enable overrepresentation analysis
        tk.Checkbutton(
            overrep_frame,
            text="Enable overrepresentation analysis",
            variable=self.overrepresentation_analysis_var,
        ).pack(anchor="w", pady=(0, 10))

        # Sampling rate
        sampling_frame = tk.Frame(overrep_frame)
        sampling_frame.pack(fill="x")

        tk.Label(sampling_frame, text="Sampling Rate:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(
            sampling_frame, textvariable=self.overrepresentation_sampling_var, width=10
        ).pack(side="left", padx=(10, 0))
        tk.Label(
            sampling_frame, text="(1 in N reads analyzed)", font=("Arial", 9), fg="gray"
        ).pack(side="left", padx=(10, 0))

    def _create_deduplication_section(self) -> None:
        """Create the deduplication options section"""
        dedup_frame = tk.LabelFrame(
            self.main_frame, text="Deduplication Options", padx=15, pady=10
        )
        dedup_frame.pack(fill="x", pady=(0, 15))

        # Accuracy level
        accuracy_frame = tk.Frame(dedup_frame)
        accuracy_frame.pack(fill="x", pady=(0, 10))

        tk.Label(accuracy_frame, text="Accuracy Level:", width=15, anchor="w").pack(
            side="left"
        )
        accuracy_combo = ttk.Combobox(
            accuracy_frame,
            textvariable=self.dup_calc_accuracy_var,
            width=10,
            values=["1", "2", "3", "4", "5", "6"],
            state="readonly",
        )
        accuracy_combo.pack(side="left", padx=(10, 20))
        tk.Label(
            accuracy_frame,
            text="(1=1G, 2=2G, 3=4G, 4=8G, 5=16G, 6=24G)",
            font=("Arial", 9),
            fg="gray",
        ).pack(side="left")

        # Don't evaluate duplication
        tk.Checkbutton(
            dedup_frame,
            text="Don't evaluate duplication rate (faster, less memory)",
            variable=self.dont_eval_duplication_var,
        ).pack(anchor="w")

    def _create_output_splitting_section(self) -> None:
        """Create the output splitting section"""
        split_frame = tk.LabelFrame(
            self.main_frame, text="Output Splitting", padx=15, pady=10
        )
        split_frame.pack(fill="x", pady=(0, 15))

        # Split by file count
        split_count_frame = tk.Frame(split_frame)
        split_count_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            split_count_frame, text="Split File Count:", width=15, anchor="w"
        ).pack(side="left")
        tk.Entry(split_count_frame, textvariable=self.split_var, width=10).pack(
            side="left", padx=(10, 20)
        )
        tk.Label(
            split_count_frame, text="(0=disabled, 2-999)", font=("Arial", 9), fg="gray"
        ).pack(side="left")

        # Split by lines
        split_lines_frame = tk.Frame(split_frame)
        split_lines_frame.pack(fill="x", pady=(0, 10))

        tk.Label(split_lines_frame, text="Split by Lines:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(
            split_lines_frame, textvariable=self.split_by_lines_var, width=10
        ).pack(side="left", padx=(10, 20))
        tk.Label(
            split_lines_frame, text="(0=disabled, >=1000)", font=("Arial", 9), fg="gray"
        ).pack(side="left")

        # Prefix digits
        prefix_frame = tk.Frame(split_frame)
        prefix_frame.pack(fill="x")

        tk.Label(prefix_frame, text="Prefix Digits:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Spinbox(
            prefix_frame,
            from_=1,
            to=10,
            textvariable=self.split_prefix_digits_var,
            width=10,
        ).pack(side="left", padx=(10, 20))
        tk.Label(
            prefix_frame, text="(padding for 0001.xxx)", font=("Arial", 9), fg="gray"
        ).pack(side="left")

    def _create_report_options_section(self) -> None:
        """Create the report options section"""
        report_frame = tk.LabelFrame(
            self.main_frame, text="Report Options", padx=15, pady=10
        )
        report_frame.pack(fill="x", pady=(0, 15))

        # Report title
        title_frame = tk.Frame(report_frame)
        title_frame.pack(fill="x")

        tk.Label(title_frame, text="Report Title:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(title_frame, textvariable=self.report_title_var).pack(
            side="left", padx=(10, 10), fill="x", expand=True
        )

    def _create_additional_io_section(self) -> None:
        """Create the additional I/O options section"""
        io_frame = tk.LabelFrame(
            self.main_frame, text="Additional I/O Options", padx=15, pady=10
        )
        io_frame.pack(fill="x", pady=(0, 15))

        # Boolean options
        tk.Checkbutton(io_frame, text="Verbose output", variable=self.verbose_var).pack(
            anchor="w", pady=(0, 5)
        )

        tk.Checkbutton(
            io_frame,
            text="Interleaved input (contains both R1 and R2)",
            variable=self.interleaved_in_var,
        ).pack(anchor="w", pady=(0, 5))

        # UMI delimiter
        umi_delim_frame = tk.Frame(io_frame)
        umi_delim_frame.pack(fill="x", pady=(5, 0))

        tk.Label(umi_delim_frame, text="UMI Delimiter:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(umi_delim_frame, textvariable=self.umi_delim_var, width=10).pack(
            side="left", padx=(10, 20)
        )
        tk.Label(
            umi_delim_frame,
            text="(delimiter between read name and UMI)",
            font=("Arial", 9),
            fg="gray",
        ).pack(side="left")

    def _create_index_filtering_section(self) -> None:
        """Create the index filtering section"""
        index_frame = tk.LabelFrame(
            self.main_frame, text="Index Filtering", padx=15, pady=10
        )
        index_frame.pack(fill="x", pady=(0, 15))

        # Index1 filtering
        index1_frame = tk.Frame(index_frame)
        index1_frame.pack(fill="x", pady=(0, 5))

        tk.Label(index1_frame, text="Index1 Filter File:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Button(
            index1_frame, text="Browse", command=self._browse_index1_filter, padx=15
        ).pack(side="right")
        tk.Entry(index1_frame, textvariable=self.filter_by_index1_var).pack(
            side="left", padx=(10, 10), fill="x", expand=True
        )

        # Index2 filtering
        index2_frame = tk.Frame(index_frame)
        index2_frame.pack(fill="x", pady=(0, 10))

        tk.Label(index2_frame, text="Index2 Filter File:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Button(
            index2_frame, text="Browse", command=self._browse_index2_filter, padx=15
        ).pack(side="right")
        tk.Entry(index2_frame, textvariable=self.filter_by_index2_var).pack(
            side="left", padx=(10, 10), fill="x", expand=True
        )

        # Threshold
        threshold_frame = tk.Frame(index_frame)
        threshold_frame.pack(fill="x")

        tk.Label(threshold_frame, text="Filter Threshold:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(
            threshold_frame, textvariable=self.filter_by_index_threshold_var, width=10
        ).pack(side="left", padx=(10, 20))
        tk.Label(
            threshold_frame,
            text="(allowed differences, 0=exact match)",
            font=("Arial", 9),
            fg="gray",
        ).pack(side="left")

    def _create_run_section(self) -> None:
        """Create the run section with status and progress"""
        run_frame = tk.Frame(self.main_frame)
        run_frame.pack(fill="x", pady=(15, 0))

        # Status label
        self.status_label = tk.Label(
            run_frame,
            text="Ready to run FastP preprocessing",
            font=("Arial", 10),
            fg="green",
        )
        self.status_label.pack(pady=(0, 10))

        # Progress bar
        self.progress_bar = ttk.Progressbar(run_frame, mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=(0, 15))
        self.progress_bar.pack_forget()

        # Run button
        self.run_button = tk.Button(
            run_frame,
            text="▶ Run FastP Preprocessing",
            command=self._run_fastp,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            pady=15,
        )
        self.run_button.pack(fill="x")

        # Log file monitor
        self._log_monitor_panel = LogFileMonitor(
            self.main_frame, file_path=self._fastp_log_file, height=12, width=100
        )
        self._log_monitor_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def _add_files(self) -> None:
        """Add individual files to the input list"""
        files = filedialog.askopenfilenames(
            title="Select FASTQ files",
            filetypes=[
                ("All supported", "*.fastq *.fq *.fastq.gz *.fq.gz"),
                ("FASTQ files", "*.fastq *.fq"),
                ("Compressed FASTQ", "*.fastq.gz *.fq.gz"),
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
            title="Select directory containing FASTQ files"
        )
        if not directory:
            return

        supported_extensions = (".fastq", ".fq", ".fastq.gz", ".fq.gz")
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
                "No Files", "No supported FASTQ files found in directory"
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

    def _browse_merged_out(self) -> None:
        """Browse for merged output file"""
        file = filedialog.asksaveasfilename(
            title="Select merged output file",
            filetypes=[
                ("FASTQ files", "*.fastq *.fq *.fastq.gz *.fq.gz"),
                ("All files", "*.*"),
            ],
        )
        if file:
            self.merged_out_var.set(file)

    def _browse_failed_out(self) -> None:
        """Browse for failed reads output file"""
        file = filedialog.asksaveasfilename(
            title="Select failed reads output file",
            filetypes=[
                ("FASTQ files", "*.fastq *.fq *.fastq.gz *.fq.gz"),
                ("All files", "*.*"),
            ],
        )
        if file:
            self.failed_out_var.set(file)

    def _update_status(self) -> None:
        """Update the status label based on current state"""
        if not self.status_label:
            return

        file_count = len(self.input_files)
        if file_count == 0:
            self.status_label.config(text="No files selected", fg="gray")
        elif file_count == 1:
            self.status_label.config(text="Ready to process 1 file", fg="green")
        elif file_count == 2:
            self.status_label.config(
                text="Ready to process 1 paired-end sample (2 files)", fg="green"
            )
        else:
            self.status_label.config(
                text=(
                    f"Ready to process first 2 files ({file_count} total selected - "
                    "FastP only processes one pair at a time)"
                )
            )

    def _run_fastp(self) -> None:
        """Run FastP preprocessing"""
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

            # Determine how to group files
            file_pairs = self._group_input_files()

            if not file_pairs:
                messagebox.showerror("Error", "No valid file pairs found")
                return

            # Show confirmation for multiple pairs
            if len(file_pairs) > 1:
                result = messagebox.askyesno(
                    "Multiple Files",
                    f"Found {len(file_pairs)} file pair(s) to process. Continue?",
                )
                if not result:
                    return

            # Record start time
            self.start_time = time.time()

            # Update UI for running state
            self._set_running_state(True)

            # Process all file pairs sequentially
            self._process_file_pairs(file_pairs, 0)

        except Exception as e:
            self._on_fastp_complete(False, e)

    def _group_input_files(self) -> List[dict]:
        """Group input files into pairs or singles"""
        file_pairs = []

        # Try to detect paired files automatically
        processed_files = set()

        for i, file1 in enumerate(self.input_files):
            if file1 in processed_files:
                continue

            # Look for a paired file
            file1_base = os.path.basename(file1)
            pair_file = None

            # Try different pairing patterns
            for _, file2 in enumerate(self.input_files[i + 1 :], i + 1):
                if file2 in processed_files:
                    continue

                file2_base = os.path.basename(file2)

                # Check if files are paired
                if self._are_files_paired(file1_base, file2_base):
                    pair_file = file2
                    break

            if pair_file:
                # Paired-end
                file_pairs.append(
                    {"type": "paired", "read1": file1, "read2": pair_file}
                )
                processed_files.add(file1)
                processed_files.add(pair_file)
            else:
                # Single-end
                file_pairs.append({"type": "single", "read1": file1})
                processed_files.add(file1)

        return file_pairs

    def _are_files_paired(self, file1: str, file2: str) -> bool:
        """Check if two files are likely paired"""
        # Remove extensions
        base1 = (
            file1.replace(".fastq.gz", "")
            .replace(".fq.gz", "")
            .replace(".fastq", "")
            .replace(".fq", "")
        )
        base2 = (
            file2.replace(".fastq.gz", "")
            .replace(".fq.gz", "")
            .replace(".fastq", "")
            .replace(".fq", "")
        )

        # Check common pairing patterns
        patterns = [
            ("_R1", "_R2"),
            ("_1", "_2"),
            (".1", ".2"),
            ("_F", "_R"),
            ("_forward", "_reverse"),
            ("_fw", "_rv"),
        ]

        for p1, p2 in patterns:
            if base1.endswith(p1) and base2.endswith(p2):
                # Check if the rest of the filename matches
                if base1[: -len(p1)] == base2[: -len(p2)]:
                    return True
            if base1.endswith(p2) and base2.endswith(p1):
                # Check reverse order too
                if base1[: -len(p2)] == base2[: -len(p1)]:
                    return True

        return False

    def _process_file_pairs(self, file_pairs: List[dict], current_index: int) -> None:
        """Process file pairs sequentially"""
        if current_index >= len(file_pairs):
            # All pairs processed successfully
            self._on_fastp_complete(True, None)
            return

        current_pair = file_pairs[current_index]

        # Update status
        if self.status_label:
            file_name = os.path.basename(current_pair["read1"])
            self.status_label.config(
                text=f"Processing pair {current_index + 1}/{len(file_pairs)}: {file_name}",
                fg="blue",
            )

        try:
            # Build command for current pair
            command = self._build_fastp_command_for_pair(current_pair)

            # Run FastP for this pair
            thread = LambdaThreadRunner(
                target_function=lambda: self._library_manager.run_fastp_command(
                    command
                ),
                on_success=lambda result: self._on_pair_complete(
                    True, None, file_pairs, current_index
                ),
                on_error=lambda error: self._on_pair_complete(
                    False, error, file_pairs, current_index
                ),
            )
            thread.start()

        except Exception as e:
            self._on_pair_complete(False, e, file_pairs, current_index)

    def _build_fastp_command_for_pair(self, file_pair: dict) -> List[str]:
        """Build FastP command for a specific file pair"""
        command = []

        # Input files
        command.extend(["-i", file_pair["read1"]])
        if file_pair["type"] == "paired" and "read2" in file_pair:
            command.extend(["-I", file_pair["read2"]])

        # Generate output file names
        if self.output_dir.get():
            output_dir = self.output_dir.get()
            base_name = os.path.splitext(os.path.basename(file_pair["read1"]))[0]
            if base_name.endswith(".fastq") or base_name.endswith(".fq"):
                base_name = os.path.splitext(base_name)[0]

            out1 = os.path.join(output_dir, f"{base_name}.fastp.fq")
            command.extend(["-o", out1])

            if file_pair["type"] == "paired":
                # Generate read2 output name
                base_name_r2 = base_name
                if "_R1" in base_name:
                    base_name_r2 = base_name.replace("_R1", "_R2")
                elif "_1" in base_name:
                    base_name_r2 = base_name.replace("_1", "_2")
                elif ".1" in base_name:
                    base_name_r2 = base_name.replace(".1", ".2")
                elif "_F" in base_name:
                    base_name_r2 = base_name.replace("_F", "_R")
                else:
                    base_name_r2 = f"{base_name}_R2"

                out2 = os.path.join(output_dir, f"{base_name_r2}.fastp.fq")
                command.extend(["-O", out2])

        # Add all the other options (threads, compression, etc.)
        # Copy the rest of the logic from your current _build_fastp_command method
        # ... (all the other option building code)

        # Threads
        threads = int(self.threads_var.get())
        if threads > 1:
            command.extend(["-w", str(threads)])

        # Compression
        compression = int(self.compression_var.get())
        if compression != 4:  # Default is 4
            command.extend(["-z", str(compression)])

        # Length filtering
        if not self.disable_length_filtering_var.get():
            length_required = int(self.length_required_var.get())
            if length_required != 15:  # Default is 15
                command.extend(["-l", str(length_required)])

            length_limit = int(self.length_limit_var.get())
            if length_limit > 0:
                command.extend(["--length_limit", str(length_limit)])
        else:
            command.append("-L")

        # Quality filtering
        if not self.disable_quality_filtering_var.get():
            qualified_quality = int(self.qualified_quality_var.get())
            if qualified_quality != 15:  # Default is 15
                command.extend(["-q", str(qualified_quality)])

            unqualified_percent = int(self.unqualified_percent_var.get())
            if unqualified_percent != 40:  # Default is 40
                command.extend(["-u", str(unqualified_percent)])

            n_base_limit = int(self.n_base_limit_var.get())
            if n_base_limit != 5:  # Default is 5
                command.extend(["-n", str(n_base_limit)])

            average_qual = int(self.average_qual_var.get())
            if average_qual > 0:  # Default is 0 (disabled)
                command.extend(["-e", str(average_qual)])
        else:
            command.append("-Q")

        # Global trimming
        trim_front1 = int(self.trim_front1_var.get())
        if trim_front1 > 0:
            command.extend(["-f", str(trim_front1)])

        trim_tail1 = int(self.trim_tail1_var.get())
        if trim_tail1 > 0:
            command.extend(["-t", str(trim_tail1)])

        max_len1 = int(self.max_len1_var.get())
        if max_len1 > 0:
            command.extend(["-b", str(max_len1)])

        if file_pair["type"] == "paired":
            trim_front2 = int(self.trim_front2_var.get())
            if trim_front2 > 0:
                command.extend(["-F", str(trim_front2)])

            trim_tail2 = int(self.trim_tail2_var.get())
            if trim_tail2 > 0:
                command.extend(["-T", str(trim_tail2)])

            max_len2 = int(self.max_len2_var.get())
            if max_len2 > 0:
                command.extend(["-B", str(max_len2)])

        # Adapter trimming
        if self.disable_adapter_trimming_var.get():
            command.append("-A")
        else:
            if self.adapter_sequence_var.get():
                command.extend(["-a", self.adapter_sequence_var.get()])

            if file_pair["type"] == "paired" and self.adapter_sequence_r2_var.get():
                command.extend(
                    ["--adapter_sequence_r2", self.adapter_sequence_r2_var.get()]
                )

            if file_pair["type"] == "paired" and self.detect_adapter_for_pe_var.get():
                command.append("--detect_adapter_for_pe")

        # Quality cutting
        if self.cut_front_var.get():
            command.append("-5")

        if self.cut_tail_var.get():
            command.append("-3")

        if self.cut_right_var.get():
            command.append("-r")

        # Advanced quality cutting parameters (specific per operation)
        if self.cut_front_var.get():
            # Use front-specific parameters if provided, otherwise fall back to global
            front_window_size = self.cut_front_window_size_var.get().strip()
            if (
                front_window_size and front_window_size != "4"
            ):  # Only if non-default and specified
                command.extend(["--cut_front_window_size", front_window_size])
            elif not front_window_size:  # Use global if front-specific not specified
                cut_window_size = int(self.cut_window_size_var.get())
                if cut_window_size != 4:
                    command.extend(["--cut_front_window_size", str(cut_window_size)])

            front_mean_quality = self.cut_front_mean_quality_var.get().strip()
            if (
                front_mean_quality and front_mean_quality != "20"
            ):  # Only if non-default and specified
                command.extend(["--cut_front_mean_quality", front_mean_quality])
            elif not front_mean_quality:  # Use global if front-specific not specified
                cut_mean_quality = int(self.cut_mean_quality_var.get())
                if cut_mean_quality != 20:
                    command.extend(["--cut_front_mean_quality", str(cut_mean_quality)])

        if self.cut_tail_var.get():
            # Use tail-specific parameters if provided, otherwise fall back to global
            tail_window_size = self.cut_tail_window_size_var.get().strip()
            if (
                tail_window_size and tail_window_size != "4"
            ):  # Only if non-default and specified
                command.extend(["--cut_tail_window_size", tail_window_size])
            elif not tail_window_size:  # Use global if tail-specific not specified
                cut_window_size = int(self.cut_window_size_var.get())
                if cut_window_size != 4:
                    command.extend(["--cut_tail_window_size", str(cut_window_size)])

            tail_mean_quality = self.cut_tail_mean_quality_var.get().strip()
            if (
                tail_mean_quality and tail_mean_quality != "20"
            ):  # Only if non-default and specified
                command.extend(["--cut_tail_mean_quality", tail_mean_quality])
            elif not tail_mean_quality:  # Use global if tail-specific not specified
                cut_mean_quality = int(self.cut_mean_quality_var.get())
                if cut_mean_quality != 20:
                    command.extend(["--cut_tail_mean_quality", str(cut_mean_quality)])

        if self.cut_right_var.get():
            # Use right-specific parameters if provided, otherwise fall back to global
            right_window_size = self.cut_right_window_size_var.get().strip()
            if (
                right_window_size and right_window_size != "4"
            ):  # Only if non-default and specified
                command.extend(["--cut_right_window_size", right_window_size])
            elif not right_window_size:  # Use global if right-specific not specified
                cut_window_size = int(self.cut_window_size_var.get())
                if cut_window_size != 4:
                    command.extend(["--cut_right_window_size", str(cut_window_size)])

            right_mean_quality = self.cut_right_mean_quality_var.get().strip()
            if (
                right_mean_quality and right_mean_quality != "20"
            ):  # Only if non-default and specified
                command.extend(["--cut_right_mean_quality", right_mean_quality])
            elif not right_mean_quality:  # Use global if right-specific not specified
                cut_mean_quality = int(self.cut_mean_quality_var.get())
                if cut_mean_quality != 20:
                    command.extend(["--cut_right_mean_quality", str(cut_mean_quality)])

        # Legacy global parameters (kept for backward compatibility when no specific cutting is enabled)
        if (
            self.cut_front_var.get()
            or self.cut_tail_var.get()
            or self.cut_right_var.get()
        ) and not any(
            [
                self.cut_front_window_size_var.get().strip(),
                self.cut_tail_window_size_var.get().strip(),
                self.cut_right_window_size_var.get().strip(),
                self.cut_front_mean_quality_var.get().strip(),
                self.cut_tail_mean_quality_var.get().strip(),
                self.cut_right_mean_quality_var.get().strip(),
            ]
        ):
            # Only use global -W and -M if no advanced parameters are specified
            cut_window_size = int(self.cut_window_size_var.get())
            if cut_window_size != 4:  # Default is 4
                command.extend(["-W", str(cut_window_size)])

            cut_mean_quality = int(self.cut_mean_quality_var.get())
            if cut_mean_quality != 20:  # Default is 20
                command.extend(["-M", str(cut_mean_quality)])

        # PolyG trimming
        if not self.trim_poly_g_var.get():
            command.append("-G")  # Disable polyG trimming
        else:
            poly_g_min_len = int(self.poly_g_min_len_var.get())
            # if poly_g_min_len != 10:  # Default is 10
            command.extend(["--poly_g_min_len", str(poly_g_min_len)])

        # PolyX trimming
        if self.trim_poly_x_var.get():
            command.append("-x")
            poly_x_min_len = int(self.poly_x_min_len_var.get())
            if poly_x_min_len != 10:  # Default is 10
                command.extend(["--poly_x_min_len", str(poly_x_min_len)])

        # Low complexity filter
        if self.low_complexity_filter_var.get():
            command.append("-y")
            complexity_threshold = int(self.complexity_threshold_var.get())
            if complexity_threshold != 30:  # Default is 30
                command.extend(["-Y", str(complexity_threshold)])

        # Deduplication
        if self.dedup_var.get():
            command.append("-D")

        # Base correction
        if self.correction_var.get():
            command.append("-c")

        # Merge paired-end reads
        if self.merge_var.get() and file_pair["type"] == "paired":
            command.append("-m")
            if self.merged_out_var.get():
                command.extend(["--merged_out", self.merged_out_var.get()])

        # Additional output files
        if self.failed_out_var.get():
            command.extend(["--failed_out", self.failed_out_var.get()])

        # HTML and JSON reports
        if self.output_dir.get():
            base_name = "fastp_report"
            # Use the current file pair instead of self.input_files[0]
            file_base = os.path.splitext(os.path.basename(file_pair["read1"]))[0]
            if file_base.endswith(".fastq") or file_base.endswith(".fq"):
                file_base = os.path.splitext(file_base)[0]

            # Remove paired-end suffixes for cleaner report names
            paired_suffixes = [
                "_R1",
                "_R2",
                "_1",
                "_2",
                ".1",
                ".2",
                "_F",
                "_R",
                "_forward",
                "_reverse",
                "_fw",
                "_rv",
            ]
            for suffix in paired_suffixes:
                if file_base.endswith(suffix):
                    file_base = file_base[: -len(suffix)]
                    break

            base_name = f"fastp_{file_base}"

            html_report = os.path.join(self.output_dir.get(), f"{base_name}.html")
            json_report = os.path.join(self.output_dir.get(), f"{base_name}.json")
            command.extend(["-h", html_report, "-j", json_report])

        # Additional I/O options
        if self.unpaired1_var.get():
            command.extend(["--unpaired1", self.unpaired1_var.get()])
        if self.unpaired2_var.get():
            command.extend(["--unpaired2", self.unpaired2_var.get()])
        if self.overlapped_out_var.get():
            command.extend(["--overlapped_out", self.overlapped_out_var.get()])
        if self.include_unmerged_var.get():
            command.append("--include_unmerged")
        if self.phred64_var.get():
            command.append("--phred64")
        if self.reads_to_process_var.get() != "0":
            command.extend(["--reads_to_process", self.reads_to_process_var.get()])
        if self.dont_overwrite_var.get():
            command.append("--dont_overwrite")
        if self.fix_mgi_id_var.get():
            command.append("--fix_mgi_id")

        # Advanced adapter options
        if self.adapter_fasta_var.get():
            command.extend(["--adapter_fasta", self.adapter_fasta_var.get()])
        if self.allow_gap_overlap_var.get():
            command.append("--allow_gap_overlap_trimming")

        # UMI options
        if self.umi_var.get():
            command.append("--umi")
            if self.umi_loc_var.get():
                command.extend(["--umi_loc", self.umi_loc_var.get()])
            if self.umi_len_var.get() != "0":
                command.extend(["--umi_len", self.umi_len_var.get()])
            if self.umi_prefix_var.get():
                command.extend(["--umi_prefix", self.umi_prefix_var.get()])
            if self.umi_skip_var.get() != "0":
                command.extend(["--umi_skip", self.umi_skip_var.get()])

        # Overlap correction settings
        if self.overlap_len_require_var.get() != "30":
            command.extend(
                ["--overlap_len_require", self.overlap_len_require_var.get()]
            )
        if self.overlap_diff_limit_var.get() != "5":
            command.extend(["--overlap_diff_limit", self.overlap_diff_limit_var.get()])
        if self.overlap_diff_percent_limit_var.get() != "20":
            command.extend(
                [
                    "--overlap_diff_percent_limit",
                    self.overlap_diff_percent_limit_var.get(),
                ]
            )

        # Overrepresentation analysis
        if self.overrepresentation_analysis_var.get():
            command.append("--overrepresentation_analysis")
            if self.overrepresentation_sampling_var.get() != "20":
                command.extend(
                    [
                        "--overrepresentation_sampling",
                        self.overrepresentation_sampling_var.get(),
                    ]
                )

        # Report options - auto-generate title based on input file
        # Get base name and remove paired-end suffixes for consistent naming
        report_base_name = os.path.splitext(os.path.basename(file_pair["read1"]))[0]
        if report_base_name.endswith(".fastq") or report_base_name.endswith(".fq"):
            report_base_name = os.path.splitext(report_base_name)[0]

        # Remove paired-end suffixes for cleaner report title
        paired_suffixes = [
            "_R1",
            "_R2",
            "_1",
            "_2",
            ".1",
            ".2",
            "_F",
            "_R",
            "_forward",
            "_reverse",
            "_fw",
            "_rv",
        ]
        for suffix in paired_suffixes:
            if report_base_name.endswith(suffix):
                report_base_name = report_base_name[: -len(suffix)]
                break

        # Use auto-generated title or user-specified title
        if self.report_title_var.get() == "fastp report":
            # Auto-generate title based on file name
            auto_title = f"{report_base_name}_report"
            command.extend(["--report_title", auto_title])
        else:
            # Use user-specified title
            command.extend(["--report_title", self.report_title_var.get()])

        # Deduplication options
        if self.dup_calc_accuracy_var.get() != "1":
            command.extend(["--dup_calc_accuracy", self.dup_calc_accuracy_var.get()])
        if self.dont_eval_duplication_var.get():
            command.append("--dont_eval_duplication")

        # Output splitting
        if self.split_var.get() != "0":
            command.extend(["--split", self.split_var.get()])
        if self.split_by_lines_var.get() != "0":
            command.extend(["--split_by_lines", self.split_by_lines_var.get()])
        if self.split_prefix_digits_var.get() != "4":
            command.extend(
                ["--split_prefix_digits", self.split_prefix_digits_var.get()]
            )

        return command

    def _on_pair_complete(
        self,
        success: bool,
        error: Optional[Exception],
        file_pairs: List[dict],
        current_index: int,
    ) -> None:
        """Handle completion of a single pair"""
        if success:
            # Move to next pair
            self._process_file_pairs(file_pairs, current_index + 1)
        else:
            # Stop processing on error
            self._on_fastp_complete(False, error)

    def _set_running_state(self, running: bool) -> None:
        """Set UI state for running/not running"""
        if self.run_button:
            self.run_button.config(state="disabled" if running else "normal")

        if self.status_label:
            if running:
                self.status_label.config(
                    text="Running FastP preprocessing...", fg="blue"
                )
            else:
                self._update_status()

        if self.progress_bar:
            if running:
                if self.run_button:
                    self.progress_bar.pack(
                        fill="x", pady=(0, 15), before=self.run_button
                    )
                else:
                    self.progress_bar.pack(fill="x", pady=(0, 15))
                self.progress_bar.start()
            else:
                self.progress_bar.stop()
                self.progress_bar.pack_forget()

        if self._log_monitor_panel:
            if running:
                self._log_monitor_panel.toggle_content()
            else:
                self._log_monitor_panel.toggle_content()

    def _format_elapsed_time(self, elapsed_seconds: float) -> str:
        """Format elapsed time as minutes and seconds"""
        minutes = int(elapsed_seconds // 60)
        seconds = int(elapsed_seconds % 60)

        if minutes > 0:
            return f"{minutes} minute(s) and {seconds} second(s)"
        else:
            return f"{seconds} second(s)"

    def _on_fastp_complete(self, success: bool, error: Optional[Exception]) -> None:
        """Handle FastP completion"""
        self._set_running_state(False)

        if success:
            # Calculate elapsed time
            elapsed_time = ""
            if self.start_time is not None:
                elapsed_seconds = time.time() - self.start_time
                elapsed_time = (
                    f"\n\nProcessing time: {self._format_elapsed_time(elapsed_seconds)}"
                )

            if self.status_label:
                self.status_label.config(
                    text="FastP preprocessing completed successfully!", fg="green"
                )

            success_message = (
                f"FastP preprocessing completed successfully!{elapsed_time}"
            )
            messagebox.showinfo("Success", success_message)
        else:
            if self.status_label:
                self.status_label.config(text="FastP preprocessing failed", fg="red")
            error_msg = (
                f"FastP preprocessing failed: {str(error)}"
                if error
                else "FastP preprocessing failed"
            )
            messagebox.showerror("Error", error_msg)

    def _browse_index1_filter(self) -> None:
        """Browse for index1 filter file"""
        file = filedialog.askopenfilename(
            title="Select index1 filter file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file:
            self.filter_by_index1_var.set(file)

    def _browse_index2_filter(self) -> None:
        """Browse for index2 filter file"""
        file = filedialog.askopenfilename(
            title="Select index2 filter file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file:
            self.filter_by_index2_var.set(file)
