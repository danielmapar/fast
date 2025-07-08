import os
import platform
import shutil
import tarfile
import urllib.request
import zipfile

from app.logger.config import Logger, LogType
from app.subprocess.manager import SubprocessManager


class LibraryDownloader:
    def __init__(
        self, download_dir, jdk_path, fastqc_path, perl_path, fastp_path, conda_path
    ):

        # Loggers
        self._logger = Logger().get_logger(LogType.INSTALLING_LIBRARIES)
        self._subprocess_manager = SubprocessManager(self._logger)

        # Download directory
        self._download_dir = download_dir

        # Create download directory if it doesn't exist
        os.makedirs(self._download_dir, exist_ok=True)

        # Remove all libraries if FORCE_FRESH_LIBRARY_INSTALL is true
        if os.environ.get("FORCE_FRESH_LIBRARY_INSTALL") == "true":
            self._remove_all_libraries()

        # FastQC dependencies
        self._jdk_path = jdk_path
        self._fastqc_path = fastqc_path
        self._perl_path = perl_path

        # FastP dependencies
        self._fastp_path = fastp_path

        # HybPiper dependencies
        self._conda_path = conda_path

    def _remove_all_libraries(self) -> None:
        # Remove all files inside the download directory
        self._logger.info(
            "Removing all files inside the download directory at: %s",
            self._download_dir,
        )
        for file in os.listdir(self._download_dir):
            if os.path.isfile(os.path.join(self._download_dir, file)):
                os.remove(os.path.join(self._download_dir, file))
            elif os.path.isdir(os.path.join(self._download_dir, file)):
                shutil.rmtree(os.path.join(self._download_dir, file))

    def install_all_libraries(self) -> bool:

        if os.environ.get("IGNORE_LIBRARY_INSTALL") == "true":
            return True

        self._logger.info("--------------------------------------------")
        self._logger.info("------- Installing all libraries -----------")
        self._logger.info("--------------------------------------------")

        if not self.download_and_extract_corretto_jdk():
            raise Exception("Failed to download and extract Amazon Corretto JDK")
        if not self.download_and_extract_fastqc():
            raise Exception("Failed to download and extract FastQC")
        if not self.download_and_extract_perl():
            raise Exception("Failed to download and extract Perl")
        if not self.download_and_extract_fastp():
            raise Exception("Failed to download and extract FastP")
        if not self.download_and_intall_conda():
            raise Exception("Failed to download and install Miniconda")
        if not self.download_and_intall_hybpiper():
            raise Exception("Failed to download and install HybPiper")

        self._logger.info("------------------------------------------------")
        self._logger.info("------- Libraries installed successfully -------")
        self._logger.info("------------------------------------------------")

        return True

    def download_and_intall_hybpiper(self) -> bool:
        """
        Detects if running on Linux x64 and downloads/extracts HybPiper to download directory
        """
        # Check if running on Linux
        if platform.system() != "Linux":
            self._logger.info(
                "Not running on Linux (detected: %s). Skipping HybPiper download.",
                platform.system(),
            )
            return False

        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ["x86_64", "amd64"]:
            self._logger.info(
                "Not running on x64 architecture (detected: %s). Skipping HybPiper download.",
                machine,
            )
            return False

        self._logger.info("Detected Linux x64. Setting up HybPiper...")

        try:
            # Add Conda Channels to install HybPiper
            self._logger.info("Adding Conda channels to install HybPiper...")
            self._subprocess_manager.run_subprocess(
                [
                    os.path.join(self._download_dir, self._conda_path, "bin", "conda"),
                    "config",
                    "--add",
                    "channels",
                    "defaults",
                ]
            )
            self._subprocess_manager.run_subprocess(
                [
                    os.path.join(self._download_dir, self._conda_path, "bin", "conda"),
                    "config",
                    "--add",
                    "channels",
                    "bioconda",
                ]
            )
            self._subprocess_manager.run_subprocess(
                [
                    os.path.join(self._download_dir, self._conda_path, "bin", "conda"),
                    "config",
                    "--add",
                    "channels",
                    "conda-forge",
                ]
            )
            self._logger.info("Added Conda channels to install HybPiper successfully.")

            # Initialize Conda
            self._logger.info("Initializing Conda...")
            self._subprocess_manager.run_subprocess(
                [
                    os.path.join(self._download_dir, self._conda_path, "bin", "conda"),
                    "init",
                ]
            )
            self._logger.info("Initialized Conda successfully.")

            # Create HybPiper conda environment
            self._logger.info("Creating HybPiper conda environment...")
            self._subprocess_manager.run_subprocess(
                [
                    os.path.join(self._download_dir, self._conda_path, "bin", "conda"),
                    "create",
                    "-y",
                    "-n",
                    "hybpiper",
                    "hybpiper",
                ]
            )
            self._logger.info("Created HybPiper conda environment successfully.")

            return True

        except Exception as e:
            self._logger.error("Error downloading or installing HybPiper: %s", e)
            return False

    def download_and_intall_conda(self) -> bool:
        """
        Detects if running on Linux x64 and downloads/extracts Miniconda to download directory
        """
        # Check if running on Linux
        if platform.system() != "Linux":
            self._logger.info(
                "Not running on Linux (detected: %s). Skipping Miniconda download.",
                platform.system(),
            )
            return False

        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ["x86_64", "amd64"]:
            self._logger.info(
                "Not running on x64 architecture (detected: %s). Skipping Miniconda download.",
                machine,
            )
            return False

        self._logger.info("Detected Linux x64. Downloading Miniconda...")

        # URL and local filename (download to download directory)
        url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        filename = os.path.join(self._download_dir, f"{self._conda_path}.sh")

        # Check if Miniconda already exists
        if os.path.exists(self._conda_path):
            self._logger.info("Miniconda already exists at: %s", self._conda_path)
            return True

        try:
            # Download the file
            self._logger.info("Downloading from %s...", url)
            self._logger.info("Saving to: %s", filename)
            urllib.request.urlretrieve(url, filename)
            self._logger.info("Downloaded %s successfully.", filename)

            # Make the file executable
            os.chmod(filename, 0o755)

            # Run the Miniconda installer
            self._logger.info("Running %s...", filename)
            self._subprocess_manager.run_subprocess(
                [
                    filename,
                    "-b",
                    "-p",
                    os.path.join(self._download_dir, self._conda_path),
                ]
            )
            self._logger.info(
                "Installed Miniconda to %s successfully.", self._download_dir
            )

            # Create HybPiper conda environment
            self._logger.info("Creating HybPiper conda environment...")
            self._subprocess_manager.run_subprocess(
                [
                    os.path.join(self._download_dir, self._conda_path, "bin", "conda"),
                    "create",
                    "-y",
                    "-n",
                    "hybpiper",
                    "hybpiper",
                ]
            )
            self._logger.info("Created HybPiper conda environment successfully.")

            return True

        except Exception as e:
            self._logger.error("Error downloading or installing Miniconda: %s", e)
            return False

    def download_and_extract_fastp(self) -> bool:
        """
        Detects if running on Linux x64 and downloads/extracts FastP to download directory
        """
        # Check if running on Linux
        if platform.system() != "Linux":
            self._logger.info(
                "Not running on Linux (detected: %s). Skipping FastP download.",
                platform.system(),
            )
            return False

        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ["x86_64", "amd64"]:
            self._logger.info(
                "Not running on x64 architecture (detected: %s). Skipping FastP download.",
                machine,
            )
            return False

        self._logger.info("Detected Linux x64. Downloading FastP...")

        # URL and local filename (download to download directory)
        url = "http://opengene.org/fastp/fastp.1.0.1"
        filename = os.path.join(self._download_dir, "fastp.1.0.1")

        # Check if FastP already exists
        if os.path.exists(self._fastp_path):
            self._logger.info("FastP already exists at: %s", self._fastp_path)
            return True

        try:
            # Download the file
            self._logger.info("Downloading from %s...", url)
            self._logger.info("Saving to: %s", filename)
            urllib.request.urlretrieve(url, filename)
            self._logger.info("Downloaded %s successfully.", filename)

            # Move the fastp file to fastp_path
            self._logger.info("Moving %s to %s...", filename, self._fastp_path)
            shutil.move(filename, self._fastp_path)
            self._logger.info("Moved FastP to %s successfully.", self._fastp_path)

            # Chmod +x the FastP executable
            os.chmod(self._fastp_path, 0o755)

            return True

        except Exception as e:
            self._logger.error("Error downloading FastP: %s", e)
            return False

    def download_and_extract_perl(self) -> bool:
        """
        Detects if running on Linux x64 and downloads/extracts relocatable Perl to download directory
        """
        # Check if running on Linux
        if platform.system() != "Linux":
            self._logger.info(
                "Not running on Linux (detected: %s). Skipping Perl download.",
                platform.system(),
            )
            return False

        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ["x86_64", "amd64"]:
            self._logger.info(
                "Not running on x64 architecture (detected: %s). Skipping Perl download.",
                machine,
            )
            return False

        self._logger.info("Detected Linux x64. Downloading relocatable Perl...")

        # URL and local filename (download to download directory)
        url = "https://github.com/skaji/relocatable-perl/releases/latest/download/perl-linux-amd64.tar.xz"
        filename = os.path.join(self._download_dir, "perl-linux-amd64.tar.xz")

        # Check if Perl already exists
        if os.path.exists(self._perl_path):
            self._logger.info("Perl already exists at: %s", self._perl_path)
            return True

        try:
            # Download the file
            self._logger.info("Downloading from %s...", url)
            self._logger.info("Saving to: %s", filename)
            urllib.request.urlretrieve(url, filename)
            self._logger.info("Downloaded %s successfully.", filename)

            # Extract the tar.xz file to download directory first
            self._logger.info("Extracting %s...", filename)
            with tarfile.open(filename, "r:xz") as tar:
                tar.extractall(path=self._download_dir)
            self._logger.info("Extracted %s successfully.", filename)

            # Move the extracted perl-linux-amd64 directory to perl_path
            extracted_dir = os.path.join(self._download_dir, "perl-linux-amd64")
            if os.path.exists(extracted_dir):
                self._logger.info("Moving %s to %s...", extracted_dir, self._perl_path)
                shutil.move(extracted_dir, self._perl_path)
                self._logger.info("Moved Perl to %s successfully.", self._perl_path)
            else:
                raise Exception("Extracted perl-linux-amd64 directory not found")

            # Clean up the downloaded archive
            os.remove(filename)
            self._logger.info("Cleaned up %s.", filename)

            return True

        except Exception as e:
            self._logger.error("Error downloading or extracting Perl: %s", e)
            # Clean up partial download if it exists
            if os.path.exists(filename):
                os.remove(filename)
            # Clean up partial extraction if it exists
            extracted_dir = os.path.join(self._download_dir, "perl-linux-amd64")
            if os.path.exists(extracted_dir):
                shutil.rmtree(extracted_dir)
            return False

    def download_and_extract_fastqc(self) -> bool:
        """
        Detects if running on Linux x64 and downloads/extracts FastQC to download directory
        """
        # Check if running on Linux
        if platform.system() != "Linux":
            self._logger.info(
                "Not running on Linux (detected: %s). Skipping FastQC download.",
                platform.system(),
            )

        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ["x86_64", "amd64"]:
            self._logger.info(
                "Not running on x64 architecture (detected: %s). Skipping FastQC download.",
                machine,
            )
            return False

        self._logger.info("Detected Linux x64. Downloading FastQC...")

        # URL and local filename (download to download directory)
        url = "https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.12.1.zip"
        filename = os.path.join(self._download_dir, "fastqc_v0.12.1.zip")

        # Check if FastQC already exists
        if os.path.exists(self._fastqc_path):
            self._logger.info("FastQC already exists at: %s", self._fastqc_path)
            return True

        try:
            # Download the file
            self._logger.info("Downloading from %s...", url)
            self._logger.info("Saving to: %s", filename)
            urllib.request.urlretrieve(url, filename)
            self._logger.info("Downloaded %s successfully.", filename)

            # Extract the zip file to fastqc_path directory
            self._logger.info("Extracting %s to %s...", filename, self._fastqc_path)
            with zipfile.ZipFile(filename, "r") as zip_ref:
                zip_ref.extractall(self._fastqc_path)
            self._logger.info("Extracted %s successfully.", filename)

            # Clean up the downloaded archive
            os.remove(filename)
            self._logger.info("Cleaned up %s.", filename)

            # Chmod +x the FastQC executable
            os.chmod(os.path.join(self._fastqc_path, "FastQC/fastqc"), 0o755)

            return True

        except Exception as e:
            self._logger.error("Error downloading or extracting FastQC: %s", e)
            # Clean up partial download if it exists
            if os.path.exists(filename):
                os.remove(filename)
            return False

    def download_and_extract_corretto_jdk(self) -> bool:
        """
        Detects if running on Linux x64 and downloads/extracts Amazon Corretto JDK to download directory
        """
        # Check if running on Linux
        if platform.system() != "Linux":
            self._logger.info(
                "Not running on Linux (detected: %s). Skipping JDK download.",
                platform.system(),
            )
            return False

        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ["x86_64", "amd64"]:
            self._logger.info(
                "Not running on x64 architecture (detected: %s). Skipping JDK download.",
                machine,
            )
            return False

        self._logger.info("Detected Linux x64. Downloading Amazon Corretto JDK...")

        # URL and local filename (download to download directory)
        url = "https://corretto.aws/downloads/latest/amazon-corretto-21-x64-linux-jdk.tar.gz"
        filename = os.path.join(
            self._download_dir, "amazon-corretto-21-x64-linux-jdk.tar.gz"
        )

        # Check if JDK already exists
        if os.path.exists(self._jdk_path):
            self._logger.info(
                "Amazon Corretto JDK already exists at: %s", self._jdk_path
            )
            return True

        try:
            # Download the file
            self._logger.info("Downloading from %s...", url)
            self._logger.info("Saving to: %s", filename)
            urllib.request.urlretrieve(url, filename)
            self._logger.info("Downloaded %s successfully.", filename)

            # Extract the tar.gz file to jdk_path directory
            self._logger.info("Extracting %s to %s...", filename, self._jdk_path)
            with tarfile.open(filename, "r:gz") as tar:
                tar.extractall(path=self._jdk_path)
            self._logger.info("Extracted %s successfully.", filename)

            # Get the first directory in jdk_path
            self._logger.info("Listing contents of %s:", self._jdk_path)
            contents = os.listdir(self._jdk_path)
            directories = [
                item
                for item in contents
                if os.path.isdir(os.path.join(self._jdk_path, item))
            ]
            if directories:
                first_dir = directories[0]
            else:
                raise Exception("No directories found in JDK extraction")

            # Move all content from child dir first_dir to jdk_path
            for file in os.listdir(os.path.join(self._jdk_path, first_dir)):
                shutil.move(
                    os.path.join(self._jdk_path, first_dir, file), self._jdk_path
                )

            # Clean up the downloaded archive
            os.remove(filename)
            self._logger.info("Cleaned up %s.", filename)

            return True

        except Exception as e:
            self._logger.error("Error downloading or extracting JDK: %s", e)
            # Clean up partial download if it exists
            if os.path.exists(filename):
                os.remove(filename)
            return False
