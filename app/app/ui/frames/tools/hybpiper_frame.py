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


class HybPiperFrame(BaseFrame):
    def __init__(self, notebook: ttk.Notebook) -> None:
        self._library_manager = LibraryManager()
        self._hybpiper_log_file = Logger().get_log_file_path(LogType.HYBPIPER)

        # UI Variables
        self.input_files: List[str] = []
        self.target_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.prefix_var = tk.StringVar()
        self.target_type_var = tk.StringVar(value="dna")
        self.threads_var = tk.StringVar(value=str(self._detect_cpu_cores()))

        # Assembly options
        self.use_bwa_var = tk.BooleanVar(value=True)
        self.no_intronerate_var = tk.BooleanVar(value=False)
        self.no_stitched_contig_var = tk.BooleanVar(value=False)

        # Advanced options
        self.min_length_var = tk.StringVar(value="")
        self.memory_var = tk.StringVar(value="")
        self.evalue_var = tk.StringVar(value="1e-5")
        self.identity_threshold_var = tk.StringVar(value="60")

        # Trio binning options
        self.paternal_kmers = tk.StringVar()
        self.maternal_kmers = tk.StringVar()

        # NEW: Read Mapping Options
        self.use_diamond_var = tk.BooleanVar(value=False)
        self.diamond_sensitivity_var = tk.StringVar(value="")
        self.max_target_seqs_var = tk.StringVar(value="")
        self.distribute_low_mem_var = tk.BooleanVar(value=False)

        # NEW: Extended Assembly Options
        self.cov_cutoff_var = tk.StringVar(value="")
        self.single_cell_assembly_var = tk.BooleanVar(value=False)
        self.kvals_var = tk.StringVar(value="")
        self.merged_var = tk.BooleanVar(value=False)
        self.timeout_assemble_reads_var = tk.StringVar(value="")

        # NEW: Contig Extraction Options
        self.not_protein_coding_var = tk.BooleanVar(value=False)
        self.blast_task_var = tk.StringVar(value="")
        self.paralog_min_length_percentage_var = tk.StringVar(value="")
        self.depth_multiplier_var = tk.StringVar(value="")
        self.target_var = tk.StringVar(value="")
        self.exclude_var = tk.StringVar(value="")
        self.timeout_extract_contigs_var = tk.StringVar(value="")
        self.no_pad_stitched_contig_gaps_var = tk.BooleanVar(value=False)
        self.chimeric_stitched_contig_check_var = tk.BooleanVar(value=False)

        # NEW: BBMap and Exonerate Options
        self.bbmap_memory_var = tk.StringVar(value="")
        self.bbmap_subfilter_var = tk.StringVar(value="")
        self.trim_hit_sliding_window_size_var = tk.StringVar(value="")
        self.exonerate_hit_sliding_window_thresh_var = tk.StringVar(value="")
        self.exonerate_skip_frameshifts_var = tk.BooleanVar(value=False)
        self.exonerate_skip_internal_stops_var = tk.BooleanVar(value=False)
        self.exonerate_refine_full_var = tk.BooleanVar(value=False)

        # NEW: Additional Options
        self.no_padding_supercontigs_var = tk.BooleanVar(value=False)
        self.keep_intermediate_files_var = tk.BooleanVar(value=False)
        self.verbose_logging_var = tk.BooleanVar(value=False)
        self.compress_sample_folder_var = tk.BooleanVar(value=False)

        # Timing variable
        self.start_time: Optional[float] = None

        # UI Elements
        self.files_listbox: Optional[tk.Listbox] = None
        self.run_button: Optional[tk.Button] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        self.status_label: Optional[tk.Label] = None

        super().__init__(notebook, "HybPiper")

    @override
    def setup_frame(self) -> None:
        # Main content with padding
        self.main_frame = tk.Frame(self.get_scrollable_container())
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Title
        title_text = "HybPiper - Targeted Sequence Capture Assembly"
        title_label = tk.Label(
            self.main_frame, text=title_text, font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Create all sections
        self._create_input_files_section()
        self._create_target_file_section()
        self._create_output_section()
        self._create_basic_options_section()
        self._create_read_mapping_options_section()
        self._create_assembly_options_section()
        self._create_advanced_options_section()
        self._create_contig_extraction_options_section()
        self._create_trio_binning_section()
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
            self.main_frame, text="Input Read Files", padx=15, pady=10
        )
        files_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Instructions
        instructions = tk.Label(
            files_frame,
            text="Select FASTQ files (single-end or paired-end reads)",
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

    def _create_target_file_section(self) -> None:
        """Create the target file selection section"""
        target_frame = tk.LabelFrame(
            self.main_frame, text="Target File", padx=15, pady=10
        )
        target_frame.pack(fill="x", pady=(0, 15))

        # Instructions
        instructions = tk.Label(
            target_frame,
            text="Select target sequence file (FASTA format with coding sequences)",
            font=("Arial", 9),
            fg="gray",
        )
        instructions.pack(anchor="w", pady=(0, 10))

        # Target file selection
        target_file_frame = tk.Frame(target_frame)
        target_file_frame.pack(fill="x", pady=(0, 10))

        tk.Label(target_file_frame, text="Target File:", width=15, anchor="w").pack(
            side="left"
        )

        tk.Button(
            target_file_frame, text="Browse", command=self._browse_target_file, padx=15
        ).pack(side="right")

        tk.Entry(target_file_frame, textvariable=self.target_file).pack(
            side="left", padx=(10, 10), fill="x", expand=True
        )

        # Target type selection
        type_frame = tk.Frame(target_frame)
        type_frame.pack(fill="x")

        tk.Label(type_frame, text="Target Type:", width=15, anchor="w").pack(
            side="left"
        )

        type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.target_type_var,
            width=20,
            values=["dna", "aa"],
            state="readonly",
        )
        type_combo.pack(side="left", padx=(10, 0))

        tk.Label(
            type_frame,
            text="(dna: nucleotide sequences, aa: amino acid sequences)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

        # Disable mouse wheel scrolling on combobox
        type_combo.bind("<MouseWheel>", lambda e: "break")
        type_combo.bind("<Button-4>", lambda e: "break")  # Linux scroll up
        type_combo.bind("<Button-5>", lambda e: "break")  # Linux scroll down

    def _create_output_section(self) -> None:
        """Create the output directory and prefix section"""
        output_frame = tk.LabelFrame(
            self.main_frame, text="Output Configuration", padx=15, pady=10
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

        # Sample prefix
        prefix_frame = tk.Frame(output_frame)
        prefix_frame.pack(fill="x")

        tk.Label(prefix_frame, text="Sample Prefix:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(prefix_frame, textvariable=self.prefix_var, width=30).pack(
            side="left", padx=(10, 0)
        )
        tk.Label(
            prefix_frame,
            text="(identifier for output files)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

    def _create_basic_options_section(self) -> None:
        """Create the basic options section"""
        basic_frame = tk.LabelFrame(
            self.main_frame, text="Basic Options", padx=15, pady=10
        )
        basic_frame.pack(fill="x", pady=(0, 15))

        # Threads
        threads_frame = tk.Frame(basic_frame)
        threads_frame.pack(fill="x", pady=(0, 10))

        tk.Label(threads_frame, text="CPU Threads:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Spinbox(
            threads_frame, from_=1, to=16, textvariable=self.threads_var, width=10
        ).pack(side="left", padx=(10, 0))

        # BWA option (for DNA targets)
        tk.Checkbutton(
            basic_frame,
            text="Use BWA for read mapping (recommended for DNA targets)",
            variable=self.use_bwa_var,
        ).pack(anchor="w")

    def _create_read_mapping_options_section(self) -> None:
        """Create the read mapping options section"""
        mapping_frame = tk.LabelFrame(
            self.main_frame, text="Read Mapping Options", padx=15, pady=10
        )
        mapping_frame.pack(fill="x", pady=(0, 15))

        # Diamond option
        tk.Checkbutton(
            mapping_frame,
            text="Use Diamond aligner instead of BLAST (--diamond)",
            variable=self.use_diamond_var,
        ).pack(anchor="w", pady=(0, 5))

        # Diamond sensitivity
        diamond_sens_frame = tk.Frame(mapping_frame)
        diamond_sens_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            diamond_sens_frame, text="Diamond Sensitivity:", width=20, anchor="w"
        ).pack(side="left")
        sensitivity_combo = ttk.Combobox(
            diamond_sens_frame,
            textvariable=self.diamond_sensitivity_var,
            width=15,
            values=[
                "",
                "fast",
                "mid-sensitive",
                "sensitive",
                "more-sensitive",
                "very-sensitive",
                "ultra-sensitive",
            ],
            state="readonly",
        )
        sensitivity_combo.pack(side="left", padx=(10, 0))
        tk.Label(
            diamond_sens_frame,
            text="(Diamond search sensitivity level)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

        # Max target sequences
        max_target_frame = tk.Frame(mapping_frame)
        max_target_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            max_target_frame, text="Max Target Sequences:", width=20, anchor="w"
        ).pack(side="left")
        tk.Entry(
            max_target_frame, textvariable=self.max_target_seqs_var, width=10
        ).pack(side="left", padx=(10, 0))
        tk.Label(
            max_target_frame,
            text="(maximum number of target sequences to process)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

        # Distribute low memory
        tk.Checkbutton(
            mapping_frame,
            text="Distribute low memory mode (--distribute_low_mem)",
            variable=self.distribute_low_mem_var,
        ).pack(anchor="w")

    def _create_assembly_options_section(self) -> None:
        """Create the assembly options section"""
        assembly_frame = tk.LabelFrame(
            self.main_frame, text="Assembly Options", padx=15, pady=10
        )
        assembly_frame.pack(fill="x", pady=(0, 15))

        # Boolean options
        tk.Checkbutton(
            assembly_frame,
            text="Skip intron recovery (--no_intronerate)",
            variable=self.no_intronerate_var,
        ).pack(anchor="w", pady=(0, 5))

        tk.Checkbutton(
            assembly_frame,
            text="Skip stitched contig creation (--no_stitched_contig)",
            variable=self.no_stitched_contig_var,
        ).pack(anchor="w", pady=(0, 5))

        tk.Checkbutton(
            assembly_frame,
            text="Single cell assembly mode (--single_cell_assembly)",
            variable=self.single_cell_assembly_var,
        ).pack(anchor="w", pady=(0, 5))

        tk.Checkbutton(
            assembly_frame,
            text="Use merged reads (--merged)",
            variable=self.merged_var,
        ).pack(anchor="w", pady=(0, 10))

        # Coverage cutoff
        cov_cutoff_frame = tk.Frame(assembly_frame)
        cov_cutoff_frame.pack(fill="x", pady=(0, 10))

        tk.Label(cov_cutoff_frame, text="Coverage Cutoff:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(cov_cutoff_frame, textvariable=self.cov_cutoff_var, width=10).pack(
            side="left", padx=(10, 0)
        )
        tk.Label(
            cov_cutoff_frame,
            text="(minimum coverage for assembly)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

        # K-vals
        kvals_frame = tk.Frame(assembly_frame)
        kvals_frame.pack(fill="x", pady=(0, 10))

        tk.Label(kvals_frame, text="K-mer Values:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(kvals_frame, textvariable=self.kvals_var, width=20).pack(
            side="left", padx=(10, 0)
        )
        tk.Label(
            kvals_frame,
            text="(comma-separated k-mer sizes, e.g., 31,41,51)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

        # Timeout assemble reads
        timeout_assemble_frame = tk.Frame(assembly_frame)
        timeout_assemble_frame.pack(fill="x")

        tk.Label(
            timeout_assemble_frame, text="Assembly Timeout:", width=15, anchor="w"
        ).pack(side="left")
        tk.Entry(
            timeout_assemble_frame,
            textvariable=self.timeout_assemble_reads_var,
            width=10,
        ).pack(side="left", padx=(10, 0))
        tk.Label(
            timeout_assemble_frame,
            text="(timeout in seconds for assembly)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

    def _create_advanced_options_section(self) -> None:
        """Create the advanced options section"""
        advanced_frame = tk.LabelFrame(
            self.main_frame, text="Advanced Options", padx=15, pady=10
        )
        advanced_frame.pack(fill="x", pady=(0, 15))

        # Min length filter
        min_length_frame = tk.Frame(advanced_frame)
        min_length_frame.pack(fill="x", pady=(0, 10))

        tk.Label(min_length_frame, text="Min Read Length:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(min_length_frame, textvariable=self.min_length_var, width=10).pack(
            side="left", padx=(10, 0)
        )
        tk.Label(
            min_length_frame,
            text="(filter reads shorter than this)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

        # Memory limit
        memory_frame = tk.Frame(advanced_frame)
        memory_frame.pack(fill="x", pady=(0, 10))

        tk.Label(memory_frame, text="Memory Limit (GB):", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(memory_frame, textvariable=self.memory_var, width=10).pack(
            side="left", padx=(10, 0)
        )
        tk.Label(
            memory_frame,
            text="(leave empty for auto)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

        # E-value threshold
        evalue_frame = tk.Frame(advanced_frame)
        evalue_frame.pack(fill="x", pady=(0, 10))

        tk.Label(evalue_frame, text="E-value Threshold:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(evalue_frame, textvariable=self.evalue_var, width=10).pack(
            side="left", padx=(10, 0)
        )
        tk.Label(
            evalue_frame,
            text="(for BLAST searches, default: 1e-5)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

        # Identity threshold
        identity_frame = tk.Frame(advanced_frame)
        identity_frame.pack(fill="x")

        tk.Label(identity_frame, text="Identity Threshold:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Spinbox(
            identity_frame,
            from_=50,
            to=100,
            textvariable=self.identity_threshold_var,
            width=10,
        ).pack(side="left", padx=(10, 0))
        tk.Label(
            identity_frame,
            text="(% identity for sequence extraction, default: 60%)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

    def _create_contig_extraction_options_section(self) -> None:
        """Create the contig extraction options section"""
        contig_frame = tk.LabelFrame(
            self.main_frame, text="Contig Extraction Options", padx=15, pady=10
        )
        contig_frame.pack(fill="x", pady=(0, 15))

        # Boolean options
        bool_options_frame1 = tk.Frame(contig_frame)
        bool_options_frame1.pack(fill="x", pady=(0, 5))

        tk.Checkbutton(
            bool_options_frame1,
            text="Not protein coding (--not_protein_coding)",
            variable=self.not_protein_coding_var,
        ).pack(side="left", anchor="w")

        tk.Checkbutton(
            bool_options_frame1,
            text="No pad stitched contig gaps (--no_pad_stitched_contig_gaps_with_n)",
            variable=self.no_pad_stitched_contig_gaps_var,
        ).pack(side="right", anchor="w")

        bool_options_frame2 = tk.Frame(contig_frame)
        bool_options_frame2.pack(fill="x", pady=(0, 10))

        tk.Checkbutton(
            bool_options_frame2,
            text="Chimeric stitched contig check (--chimeric_stitched_contig_check)",
            variable=self.chimeric_stitched_contig_check_var,
        ).pack(side="left", anchor="w")

        # BLAST task
        blast_task_frame = tk.Frame(contig_frame)
        blast_task_frame.pack(fill="x", pady=(0, 10))

        tk.Label(blast_task_frame, text="BLAST Task:", width=15, anchor="w").pack(
            side="left"
        )
        blast_task_combo = ttk.Combobox(
            blast_task_frame,
            textvariable=self.blast_task_var,
            width=15,
            values=["", "blastn", "megablast", "dc-megablast"],
            state="readonly",
        )
        blast_task_combo.pack(side="left", padx=(10, 0))
        tk.Label(
            blast_task_frame,
            text="(BLAST task type)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

        # Paralog min length percentage
        paralog_frame = tk.Frame(contig_frame)
        paralog_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            paralog_frame, text="Paralog Min Length %:", width=15, anchor="w"
        ).pack(side="left")
        tk.Entry(
            paralog_frame, textvariable=self.paralog_min_length_percentage_var, width=10
        ).pack(side="left", padx=(10, 0))
        tk.Label(
            paralog_frame,
            text="(minimum paralog length percentage)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

        # Depth multiplier
        depth_frame = tk.Frame(contig_frame)
        depth_frame.pack(fill="x", pady=(0, 10))

        tk.Label(depth_frame, text="Depth Multiplier:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(depth_frame, textvariable=self.depth_multiplier_var, width=10).pack(
            side="left", padx=(10, 0)
        )
        tk.Label(
            depth_frame,
            text="(coverage depth multiplier)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

        # Target and exclude
        target_exclude_frame = tk.Frame(contig_frame)
        target_exclude_frame.pack(fill="x", pady=(0, 10))

        tk.Label(target_exclude_frame, text="Target Genes:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(target_exclude_frame, textvariable=self.target_var, width=20).pack(
            side="left", padx=(10, 10)
        )

        tk.Label(
            target_exclude_frame, text="Exclude Genes:", width=15, anchor="w"
        ).pack(side="left")
        tk.Entry(target_exclude_frame, textvariable=self.exclude_var, width=20).pack(
            side="left", padx=(10, 0)
        )

        # Timeout extract contigs
        timeout_extract_frame = tk.Frame(contig_frame)
        timeout_extract_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            timeout_extract_frame, text="Extract Timeout:", width=15, anchor="w"
        ).pack(side="left")
        tk.Entry(
            timeout_extract_frame,
            textvariable=self.timeout_extract_contigs_var,
            width=10,
        ).pack(side="left", padx=(10, 0))
        tk.Label(
            timeout_extract_frame,
            text="(timeout in seconds for contig extraction)",
            font=("Arial", 8),
            fg="gray",
        ).pack(side="left", padx=(10, 0))

        # BBMap options
        bbmap_frame = tk.Frame(contig_frame)
        bbmap_frame.pack(fill="x", pady=(0, 10))

        tk.Label(bbmap_frame, text="BBMap Memory:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(bbmap_frame, textvariable=self.bbmap_memory_var, width=10).pack(
            side="left", padx=(10, 10)
        )

        tk.Label(bbmap_frame, text="BBMap Subfilter:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(bbmap_frame, textvariable=self.bbmap_subfilter_var, width=10).pack(
            side="left", padx=(10, 0)
        )

        # Sliding window options
        sliding_window_frame = tk.Frame(contig_frame)
        sliding_window_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            sliding_window_frame, text="Trim Hit Window:", width=15, anchor="w"
        ).pack(side="left")
        tk.Entry(
            sliding_window_frame,
            textvariable=self.trim_hit_sliding_window_size_var,
            width=10,
        ).pack(side="left", padx=(10, 10))

        tk.Label(
            sliding_window_frame, text="Exonerate Window:", width=15, anchor="w"
        ).pack(side="left")
        tk.Entry(
            sliding_window_frame,
            textvariable=self.exonerate_hit_sliding_window_thresh_var,
            width=10,
        ).pack(side="left", padx=(10, 0))

        # Exonerate options
        exonerate_frame = tk.Frame(contig_frame)
        exonerate_frame.pack(fill="x", pady=(0, 10))

        tk.Checkbutton(
            exonerate_frame,
            text="Skip frameshifts",
            variable=self.exonerate_skip_frameshifts_var,
        ).pack(side="left", anchor="w")

        tk.Checkbutton(
            exonerate_frame,
            text="Skip internal stops",
            variable=self.exonerate_skip_internal_stops_var,
        ).pack(side="left", anchor="w", padx=(20, 0))

        tk.Checkbutton(
            exonerate_frame,
            text="Refine full",
            variable=self.exonerate_refine_full_var,
        ).pack(side="left", anchor="w", padx=(20, 0))

        # Additional options
        additional_frame = tk.Frame(contig_frame)
        additional_frame.pack(fill="x")

        tk.Checkbutton(
            additional_frame,
            text="No padding supercontigs",
            variable=self.no_padding_supercontigs_var,
        ).pack(side="left", anchor="w")

        tk.Checkbutton(
            additional_frame,
            text="Keep intermediate files",
            variable=self.keep_intermediate_files_var,
        ).pack(side="left", anchor="w", padx=(20, 0))

        tk.Checkbutton(
            additional_frame,
            text="Verbose logging",
            variable=self.verbose_logging_var,
        ).pack(side="left", anchor="w", padx=(20, 0))

        tk.Checkbutton(
            additional_frame,
            text="Compress sample folder",
            variable=self.compress_sample_folder_var,
        ).pack(side="left", anchor="w", padx=(20, 0))

    def _create_trio_binning_section(self) -> None:
        """Create the trio binning options section"""
        trio_frame = tk.LabelFrame(
            self.main_frame, text="Trio Binning (Optional)", padx=15, pady=10
        )
        trio_frame.pack(fill="x", pady=(0, 15))

        # Instructions
        instructions = tk.Label(
            trio_frame,
            text="For trio binning analysis, provide k-mer dumps from parental reads",
            font=("Arial", 9),
            fg="gray",
        )
        instructions.pack(anchor="w", pady=(0, 10))

        # Paternal k-mers
        paternal_frame = tk.Frame(trio_frame)
        paternal_frame.pack(fill="x", pady=(0, 10))

        tk.Label(paternal_frame, text="Paternal K-mers:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(paternal_frame, textvariable=self.paternal_kmers).pack(
            side="left", padx=(10, 10), fill="x", expand=True
        )
        tk.Button(
            paternal_frame, text="Browse", command=self._browse_paternal_kmers, padx=15
        ).pack(side="right")

        # Maternal k-mers
        maternal_frame = tk.Frame(trio_frame)
        maternal_frame.pack(fill="x")

        tk.Label(maternal_frame, text="Maternal K-mers:", width=15, anchor="w").pack(
            side="left"
        )
        tk.Entry(maternal_frame, textvariable=self.maternal_kmers).pack(
            side="left", padx=(10, 10), fill="x", expand=True
        )
        tk.Button(
            maternal_frame, text="Browse", command=self._browse_maternal_kmers, padx=15
        ).pack(side="right")

    def _create_run_section(self) -> None:
        """Create the run section with status and progress"""
        run_frame = tk.Frame(self.main_frame)
        run_frame.pack(fill="x", pady=(15, 0))

        # Status label
        self.status_label = tk.Label(
            run_frame,
            text="Ready to run HybPiper assembly",
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
            text="▶ Run HybPiper Assembly",
            command=self._run_hybpiper,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            pady=15,
        )
        self.run_button.pack(fill="x")

        # Log file monitor
        self._log_monitor_panel = LogFileMonitor(
            self.main_frame, file_path=self._hybpiper_log_file, height=12, width=100
        )
        self._log_monitor_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def _add_files(self) -> None:
        """Add individual files to the input list"""
        files = filedialog.askopenfilenames(
            title="Select FASTQ files",
            filetypes=[
                ("FASTQ files", "*.fastq *.fq *.fastq.gz *.fq.gz"),
                ("All files", "*.*"),
            ],
        )

        for file in files:
            if file not in self.input_files:
                self.input_files.append(file)
                if self.files_listbox:
                    self.files_listbox.insert(tk.END, os.path.basename(file))

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

    def _browse_target_file(self) -> None:
        """Browse for target file"""
        file = filedialog.askopenfilename(
            title="Select target file",
            filetypes=[
                ("FASTA files", "*.fasta *.fa *.fas *.fna"),
                ("All files", "*.*"),
            ],
        )
        if file:
            self.target_file.set(file)

    def _browse_output_dir(self) -> None:
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_dir.set(directory)

    def _browse_paternal_kmers(self) -> None:
        """Browse for paternal k-mers file"""
        file = filedialog.askopenfilename(
            title="Select paternal k-mers file",
            filetypes=[("YAK files", "*.yak"), ("All files", "*.*")],
        )
        if file:
            self.paternal_kmers.set(file)

    def _browse_maternal_kmers(self) -> None:
        """Browse for maternal k-mers file"""
        file = filedialog.askopenfilename(
            title="Select maternal k-mers file",
            filetypes=[("YAK files", "*.yak"), ("All files", "*.*")],
        )
        if file:
            self.maternal_kmers.set(file)

    def _update_status(self) -> None:
        """Update the status label based on current state"""
        if not self.status_label:
            return

        file_count = len(self.input_files)
        if file_count == 0:
            self.status_label.config(text="No read files selected", fg="gray")
        elif not self.target_file.get():
            self.status_label.config(text="Target file required", fg="orange")
        elif not self.prefix_var.get():
            self.status_label.config(text="Sample prefix required", fg="orange")
        else:
            self.status_label.config(
                text=f"Ready to assemble with {file_count} read file(s)", fg="green"
            )

    def _build_hybpiper_command(self) -> List[str]:
        """Build HybPiper command based on current UI settings"""
        if not self.input_files:
            raise ValueError("No input files selected")

        if not self.target_file.get():
            raise ValueError("No target file selected")

        if not self.prefix_var.get():
            raise ValueError("Sample prefix is required")

        command = ["hybpiper", "assemble"]

        # Target file
        target_type = self.target_type_var.get()
        if target_type == "dna":
            command.extend(["-t_dna", self.target_file.get()])
        else:
            command.extend(["-t_aa", self.target_file.get()])

        # Input reads
        command.extend(["-r"] + self.input_files)

        # Prefix
        command.extend(["--prefix", self.prefix_var.get()])

        # CPU threads
        threads = int(self.threads_var.get())
        if threads > 1:
            command.extend(["--cpu", str(threads)])

        # BWA option
        if self.use_bwa_var.get() and target_type == "dna":
            command.append("--bwa")

        # Read Mapping Options
        if self.use_diamond_var.get():
            command.append("--diamond")

        if self.diamond_sensitivity_var.get().strip():
            command.extend(
                ["--diamond_sensitivity", self.diamond_sensitivity_var.get()]
            )

        if self.max_target_seqs_var.get().strip():
            try:
                max_seqs = int(self.max_target_seqs_var.get())
                command.extend(["--max_target_seqs", str(max_seqs)])
            except ValueError:
                pass

        if self.distribute_low_mem_var.get():
            command.append("--distribute_low_mem")

        # Assembly options
        if self.no_intronerate_var.get():
            command.append("--no_intronerate")

        if self.no_stitched_contig_var.get():
            command.append("--no_stitched_contig")

        if self.single_cell_assembly_var.get():
            command.append("--single_cell_assembly")

        if self.merged_var.get():
            command.append("--merged")

        if self.cov_cutoff_var.get().strip():
            try:
                cov_cutoff = float(self.cov_cutoff_var.get())
                command.extend(["--cov_cutoff", str(cov_cutoff)])
            except ValueError:
                pass

        if self.kvals_var.get().strip():
            command.extend(["--kvals", self.kvals_var.get()])

        if self.timeout_assemble_reads_var.get().strip():
            try:
                timeout = int(self.timeout_assemble_reads_var.get())
                command.extend(["--timeout_assemble_reads", str(timeout)])
            except ValueError:
                pass

        # Advanced options
        if self.min_length_var.get().strip():
            try:
                min_length = int(self.min_length_var.get())
                command.extend(["--min_length", str(min_length)])
            except ValueError:
                pass  # Skip if invalid integer

        if self.memory_var.get().strip():
            try:
                memory = int(self.memory_var.get())
                command.extend(["--memory", str(memory)])
            except ValueError:
                pass  # Skip if invalid integer

        if self.evalue_var.get().strip() and self.evalue_var.get() != "1e-5":
            command.extend(["--evalue", self.evalue_var.get()])

        if (
            self.identity_threshold_var.get().strip()
            and self.identity_threshold_var.get() != "60"
        ):
            command.extend(["--thresh", self.identity_threshold_var.get()])

        # Contig Extraction Options
        if self.not_protein_coding_var.get():
            command.append("--not_protein_coding")

        if self.blast_task_var.get().strip():
            command.extend(["--blast_task", self.blast_task_var.get()])

        if self.paralog_min_length_percentage_var.get().strip():
            try:
                paralog_min = float(self.paralog_min_length_percentage_var.get())
                command.extend(["--paralog_min_length_percentage", str(paralog_min)])
            except ValueError:
                pass

        if self.depth_multiplier_var.get().strip():
            try:
                depth_mult = float(self.depth_multiplier_var.get())
                command.extend(["--depth_multiplier", str(depth_mult)])
            except ValueError:
                pass

        if self.target_var.get().strip():
            command.extend(["--target", self.target_var.get()])

        if self.exclude_var.get().strip():
            command.extend(["--exclude", self.exclude_var.get()])

        if self.timeout_extract_contigs_var.get().strip():
            try:
                timeout = int(self.timeout_extract_contigs_var.get())
                command.extend(["--timeout_extract_contigs", str(timeout)])
            except ValueError:
                pass

        if self.no_pad_stitched_contig_gaps_var.get():
            command.append("--no_pad_stitched_contig_gaps_with_n")

        if self.chimeric_stitched_contig_check_var.get():
            command.append("--chimeric_stitched_contig_check")

        if self.bbmap_memory_var.get().strip():
            command.extend(["--bbmap_memory", self.bbmap_memory_var.get()])

        if self.bbmap_subfilter_var.get().strip():
            try:
                subfilter = int(self.bbmap_subfilter_var.get())
                command.extend(["--bbmap_subfilter", str(subfilter)])
            except ValueError:
                pass

        if self.trim_hit_sliding_window_size_var.get().strip():
            try:
                window_size = int(self.trim_hit_sliding_window_size_var.get())
                command.extend(["--trim_hit_sliding_window_size", str(window_size)])
            except ValueError:
                pass

        if self.exonerate_hit_sliding_window_thresh_var.get().strip():
            try:
                window_thresh = float(
                    self.exonerate_hit_sliding_window_thresh_var.get()
                )
                command.extend(
                    ["--exonerate_hit_sliding_window_thresh", str(window_thresh)]
                )
            except ValueError:
                pass

        if self.exonerate_skip_frameshifts_var.get():
            command.append("--exonerate_skip_hits_with_frameshifts")

        if self.exonerate_skip_internal_stops_var.get():
            command.append("--exonerate_skip_hits_with_internal_stop_codons")

        if self.exonerate_refine_full_var.get():
            command.append("--exonerate_refine_full")

        if self.no_padding_supercontigs_var.get():
            command.append("--no_padding_supercontigs")

        if self.keep_intermediate_files_var.get():
            command.append("--keep_intermediate_files")

        if self.verbose_logging_var.get():
            command.append("--verbose_logging")

        if self.compress_sample_folder_var.get():
            command.append("--compress_sample_folder")

        # Trio binning options
        if self.paternal_kmers.get():
            command.extend(["-1", self.paternal_kmers.get()])

        if self.maternal_kmers.get():
            command.extend(["-2", self.maternal_kmers.get()])

        return command

    def _run_hybpiper(self) -> None:
        """Run HybPiper assembly"""
        try:
            # Validate inputs
            if not self.input_files:
                messagebox.showerror("Error", "Please select at least one input file")
                return

            if not self.target_file.get():
                messagebox.showerror("Error", "Please select a target file")
                return

            if not self.prefix_var.get():
                messagebox.showerror("Error", "Please provide a sample prefix")
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
            command = self._build_hybpiper_command()

            # Record start time
            self.start_time = time.time()

            # Update UI for running state
            self._set_running_state(True)

            # Run HybPiper in background thread
            thread = LambdaThreadRunner(
                target_function=lambda: self._library_manager.run_hybpiper_command(
                    command
                ),
                on_success=lambda result: self._on_hybpiper_complete(True, None),
                on_error=lambda error: self._on_hybpiper_complete(False, error),
            )
            thread.start()

        except Exception as e:
            self._on_hybpiper_complete(False, e)

    def _set_running_state(self, running: bool) -> None:
        """Set UI state for running/not running"""
        if self.run_button:
            self.run_button.config(state="disabled" if running else "normal")

        if self.status_label:
            if running:
                self.status_label.config(text="Running HybPiper assembly...", fg="blue")
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

    def _on_hybpiper_complete(self, success: bool, error: Optional[Exception]) -> None:
        """Handle HybPiper completion"""
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
                    text="HybPiper assembly completed successfully!", fg="green"
                )

            success_message = f"HybPiper assembly completed successfully!{elapsed_time}"
            messagebox.showinfo("Success", success_message)
        else:
            if self.status_label:
                self.status_label.config(text="HybPiper assembly failed", fg="red")
            error_msg = (
                f"HybPiper assembly failed: {str(error)}"
                if error
                else "HybPiper assembly failed"
            )
            messagebox.showerror("Error", error_msg)
