import os
from typing import List, Optional

import requests  # type: ignore

from app.library.downloader import LibraryDownloader
from app.library.runner import LibraryRunner


class LibraryManager:

    def __init__(self) -> None:
        download_dir_env: Optional[str] = os.getenv("DOWNLOAD_DIR")
        if download_dir_env is None:
            raise ValueError("DOWNLOAD_DIR environment variable is not set")

        jdk_version_env: Optional[str] = os.getenv("JDK_VERSION")
        if jdk_version_env is None:
            raise ValueError("JDK_VERSION environment variable is not set")

        fastqc_version_env: Optional[str] = os.getenv("FASTQC_VERSION")
        if fastqc_version_env is None:
            raise ValueError("FASTQC_VERSION environment variable is not set")

        perl_version_env: Optional[str] = os.getenv("PERL_VERSION")
        if perl_version_env is None:
            raise ValueError("PERL_VERSION environment variable is not set")

        fastp_version_env: Optional[str] = os.getenv("FASTP_VERSION")
        if fastp_version_env is None:
            raise ValueError("FASTP_VERSION environment variable is not set")

        conda_version_env: Optional[str] = os.getenv("CONDA_VERSION")
        if conda_version_env is None:
            raise ValueError("CONDA_VERSION environment variable is not set")

        self.download_dir = os.path.expanduser(download_dir_env)
        self.jdk_path = os.path.join(self.download_dir, jdk_version_env)
        self.fastqc_path = os.path.join(self.download_dir, fastqc_version_env)
        self.perl_path = os.path.join(self.download_dir, perl_version_env)
        self.fastp_path = os.path.join(self.download_dir, fastp_version_env)
        self.conda_path = os.path.join(self.download_dir, conda_version_env)

        # Library downloader
        self.library_downloader = LibraryDownloader(
            self.download_dir,
            self.jdk_path,
            self.fastqc_path,
            self.perl_path,
            self.fastp_path,
            self.conda_path,
        )

        # Library runner
        self.library_runner = LibraryRunner(
            self.jdk_path,
            self.fastqc_path,
            self.perl_path,
            self.fastp_path,
            self.conda_path,
        )

        if (
            not self.are_libraries_installed()
            and not self.is_user_connected_to_internet()
        ):
            raise Exception(
                "No internet connection and libraries are not installed! "
                "Please check your internet connection and try again."
            )

    def is_user_connected_to_internet(self) -> bool:
        try:
            response = requests.get("https://www.google.com", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def are_libraries_installed(self) -> bool:
        return len(os.listdir(self.download_dir)) != 0

    def install_libraries(self) -> None:
        try:
            self.library_downloader.install_all_libraries()
        except Exception as e:
            self.library_downloader._remove_all_libraries()
            raise Exception(f"Error while installing libraries: {e}")

    def test_libraries(self) -> None:
        try:
            self.library_runner.test_all_libraries()
        except Exception as e:
            # Remove all libraries for a possible re-install
            self.library_downloader._remove_all_libraries()
            raise Exception(f"Error while testing library installations: {e}")

    def run_fastqc_command(self, commands: List[str]) -> None:
        """
        Run FastQC command with the given arguments

        Args:
            commands: List of command line arguments for FastQC
        """
        # Set up paths
        fastqc_executable = os.path.join(self.fastqc_path, "FastQC", "fastqc")
        perl_executable = os.path.join(self.perl_path, "bin", "perl")
        jdk_executable = os.path.join(self.jdk_path, "bin", "java")

        # Verify executables exist
        if not os.path.exists(fastqc_executable):
            raise FileNotFoundError(
                f"FastQC executable not found at: {fastqc_executable}"
            )

        if not os.path.exists(perl_executable):
            raise FileNotFoundError(f"Perl executable not found at: {perl_executable}")

        if not os.path.exists(jdk_executable):
            raise FileNotFoundError(f"Java executable not found at: {jdk_executable}")

        # Build the full command
        full_command = [perl_executable, fastqc_executable, "--java", jdk_executable]
        full_command.extend(commands)

        # Create subprocess manager with appropriate logger
        from app.logger.config import Logger, LogType
        from app.subprocess.manager import SubprocessManager

        logger = Logger().get_logger(
            LogType.TESTING_LIBRARIES
        )  # We could create a specific logger for FastQC
        subprocess_manager = SubprocessManager(logger)

        # Run the command
        result = subprocess_manager.run_subprocess(full_command)

        if result.returncode != 0:
            raise RuntimeError(
                f"FastQC failed with return code {result.returncode}: {result.stderr}"
            )
