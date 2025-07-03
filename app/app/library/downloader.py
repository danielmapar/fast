import platform
import urllib.request
import tarfile
import os
import shutil
import zipfile
import logging
import subprocess

class LibraryDownloader:
    def __init__(self, download_dir, jdk_path, fastqc_path, perl_path, fastp_path, conda_path, remove_existing_files=True):
        
        self.logger = logging.getLogger()
        
        self.download_dir = download_dir
        
        self.logger.info(f"Creating download directory at: {self.download_dir}")
        os.makedirs(self.download_dir, exist_ok=True) 

        if os.environ.get("FORCE_LIBRARY_INSTALL") == "true":
            self.remove_all_libraries()

        # FastQC dependencies
        self.jdk_path = jdk_path
        self.fastqc_path = fastqc_path
        self.perl_path = perl_path

        # FastP dependencies
        self.fastp_path = fastp_path
        
        # HybPiper dependencies
        self.conda_path = conda_path

    def remove_all_libraries(self):
        # Remove all files inside the download directory
        self.logger.info(f"Removing all files inside the download directory at: {self.download_dir}")
        for file in os.listdir(self.download_dir):
            if os.path.isfile(os.path.join(self.download_dir, file)):
                os.remove(os.path.join(self.download_dir, file))
            elif os.path.isdir(os.path.join(self.download_dir, file)):
                shutil.rmtree(os.path.join(self.download_dir, file))

    def setup_all_libraries(self) -> bool:
        self.logger.info("------------------------------------------")
        self.logger.info(f"------- Setting up all libraries -------")
        self.logger.info("------------------------------------------")

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
        
        self.logger.info("------------------------------------------")
        self.logger.info(f"------- Libraries setup successfully -------")
        self.logger.info("------------------------------------------")

        return True

    def download_and_intall_hybpiper(self):
        """
        Detects if running on Linux x64 and downloads/extracts HybPiper to download directory
        """
        # Check if running on Linux
        if platform.system() != 'Linux':
            self.logger.info(f"Not running on Linux (detected: {platform.system()}). Skipping HybPiper download.")
            return False
        
        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ['x86_64', 'amd64']:
            self.logger.info(f"Not running on x64 architecture (detected: {machine}). Skipping HybPiper download.")
            return False
        
        self.logger.info("Detected Linux x64. Setting up HybPiper...")

        try:
            # Add Conda Channels to install HybPiper
            self.logger.info(f"Adding Conda channels to install HybPiper...")
            subprocess.run([os.path.join(self.download_dir, self.conda_path, "bin", "conda"), "config", "--add", "channels", "defaults"], check=True)
            subprocess.run([os.path.join(self.download_dir, self.conda_path, "bin", "conda"), "config", "--add", "channels", "bioconda"], check=True)
            subprocess.run([os.path.join(self.download_dir, self.conda_path, "bin", "conda"), "config", "--add", "channels", "conda-forge"], check=True)
            self.logger.info(f"Added Conda channels to install HybPiper successfully.")

            # Initialize Conda
            self.logger.info(f"Initializing Conda...")
            subprocess.run([os.path.join(self.download_dir, self.conda_path, "bin", "conda") , "init"], check=True)
            self.logger.info(f"Initialized Conda successfully.")
            
            # Create HybPiper conda environment
            self.logger.info(f"Creating HybPiper conda environment...")
            subprocess.run([os.path.join(self.download_dir, self.conda_path, "bin", "conda"), "create", "-y", "-n", "hybpiper", "hybpiper"], check=True)
            self.logger.info(f"Created HybPiper conda environment successfully.")
    
            return True
        
        except Exception as e:
            self.logger.error(f"Error downloading or installing HybPiper: {e}")
            return False
    
    def download_and_intall_conda(self):
        """
        Detects if running on Linux x64 and downloads/extracts Miniconda to download directory
        """
        # Check if running on Linux
        if platform.system() != 'Linux':
            self.logger.info(f"Not running on Linux (detected: {platform.system()}). Skipping Miniconda download.")
            return False
        
        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ['x86_64', 'amd64']:
            self.logger.info(f"Not running on x64 architecture (detected: {machine}). Skipping Miniconda download.")
            return False
        
        self.logger.info("Detected Linux x64. Downloading Miniconda...")
        
        # URL and local filename (download to download directory)
        url = f"https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        filename = os.path.join(self.download_dir, f"{self.conda_path}.sh")

        # Check if Miniconda already exists
        if os.path.exists(self.conda_path):
            self.logger.info(f"Miniconda already exists at: {self.conda_path}")
            return True
        
        try:
            # Download the file
            self.logger.info(f"Downloading from {url}...")
            self.logger.info(f"Saving to: {filename}")
            urllib.request.urlretrieve(url, filename)
            self.logger.info(f"Downloaded {filename} successfully.")

            # Make the file executable
            os.chmod(filename, 0o755)
            
            # Run the Miniconda installer
            self.logger.info(f"Running {filename}...")
            subprocess.run([filename, "-b", "-p", os.path.join(self.download_dir, self.conda_path)], check=True)
            self.logger.info(f"Installed Miniconda to {self.download_dir} successfully.")


            # Create HybPiper conda environment
            self.logger.info(f"Creating HybPiper conda environment...")
            subprocess.run([os.path.join(self.download_dir, self.conda_path, "bin", "conda"), "create", "-y", "-n", "hybpiper", "hybpiper"], check=True)
            self.logger.info(f"Created HybPiper conda environment successfully.")

            return True
        
        except Exception as e:
            self.logger.error(f"Error downloading or installing Miniconda: {e}")
            return False
    
    def download_and_extract_fastp(self):
        """
        Detects if running on Linux x64 and downloads/extracts FastP to download directory
        """
        # Check if running on Linux
        if platform.system() != 'Linux':
            self.logger.info(f"Not running on Linux (detected: {platform.system()}). Skipping FastP download.")
            return False
        
        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ['x86_64', 'amd64']:
            self.logger.info(f"Not running on x64 architecture (detected: {machine}). Skipping FastP download.")
            return False
        
        self.logger.info("Detected Linux x64. Downloading FastP...")
        
        # URL and local filename (download to download directory)
        url = "http://opengene.org/fastp/fastp.1.0.1"
        filename = os.path.join(self.download_dir, "fastp.1.0.1")

        # Check if FastP already exists
        if os.path.exists(self.fastp_path):
            self.logger.info(f"FastP already exists at: {self.fastp_path}")
            return True
        
        try:
            # Download the file
            self.logger.info(f"Downloading from {url}...")
            self.logger.info(f"Saving to: {filename}")
            urllib.request.urlretrieve(url, filename)
            self.logger.info(f"Downloaded {filename} successfully.")

            # Move the fastp file to fastp_path
            self.logger.info(f"Moving {filename} to {self.fastp_path}...")
            shutil.move(filename, self.fastp_path)
            self.logger.info(f"Moved FastP to {self.fastp_path} successfully.")

            # Chmod +x the FastP executable
            os.chmod(self.fastp_path, 0o755)
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error downloading FastP: {e}")
            return False
    
    def download_and_extract_perl(self):
        """
        Detects if running on Linux x64 and downloads/extracts relocatable Perl to download directory
        """
        # Check if running on Linux
        if platform.system() != 'Linux':
            self.logger.info(f"Not running on Linux (detected: {platform.system()}). Skipping Perl download.")
            return False
        
        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ['x86_64', 'amd64']:
            self.logger.info(f"Not running on x64 architecture (detected: {machine}). Skipping Perl download.")
            return False
        
        self.logger.info("Detected Linux x64. Downloading relocatable Perl...")
        
        # URL and local filename (download to download directory)
        url = "https://github.com/skaji/relocatable-perl/releases/latest/download/perl-linux-amd64.tar.xz"
        filename = os.path.join(self.download_dir, "perl-linux-amd64.tar.xz")
        
        # Check if Perl already exists
        if os.path.exists(self.perl_path):
            self.logger.info(f"Perl already exists at: {self.perl_path}")
            return True
        
        try:
            # Download the file
            self.logger.info(f"Downloading from {url}...")
            self.logger.info(f"Saving to: {filename}")
            urllib.request.urlretrieve(url, filename)
            self.logger.info(f"Downloaded {filename} successfully.")
            
            # Extract the tar.xz file to download directory first
            self.logger.info(f"Extracting {filename}...")
            with tarfile.open(filename, 'r:xz') as tar:
                tar.extractall(path=self.download_dir)
            self.logger.info(f"Extracted {filename} successfully.")
            
            # Move the extracted perl-linux-amd64 directory to perl_path
            extracted_dir = os.path.join(self.download_dir, "perl-linux-amd64")
            if os.path.exists(extracted_dir):
                self.logger.info(f"Moving {extracted_dir} to {self.perl_path}...")
                shutil.move(extracted_dir, self.perl_path)
                self.logger.info(f"Moved Perl to {self.perl_path} successfully.")
            else:
                raise Exception("Extracted perl-linux-amd64 directory not found")

            # Clean up the downloaded archive
            os.remove(filename)
            self.logger.info(f"Cleaned up {filename}.")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error downloading or extracting Perl: {e}")
            # Clean up partial download if it exists
            if os.path.exists(filename):
                os.remove(filename)
            # Clean up partial extraction if it exists
            extracted_dir = os.path.join(self.download_dir, "perl-linux-amd64")
            if os.path.exists(extracted_dir):
                shutil.rmtree(extracted_dir)
            return False
    
    def download_and_extract_fastqc(self):
        """
        Detects if running on Linux x64 and downloads/extracts FastQC to download directory
        """
        # Check if running on Linux
        if platform.system() != 'Linux':
            self.logger.info(f"Not running on Linux (detected: {platform.system()}). Skipping FastQC download.")

        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ['x86_64', 'amd64']:
            self.logger.info(f"Not running on x64 architecture (detected: {machine}). Skipping FastQC download.")
            return False
        
        self.logger.info("Detected Linux x64. Downloading FastQC...")

        # URL and local filename (download to download directory)
        url = "https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.12.1.zip"
        filename = os.path.join(self.download_dir, "fastqc_v0.12.1.zip")
        
        # Check if FastQC already exists
        if os.path.exists(self.fastqc_path):
            self.logger.info(f"FastQC already exists at: {self.fastqc_path}")
            return True
        
        try:
            # Download the file
            self.logger.info(f"Downloading from {url}...")
            self.logger.info(f"Saving to: {filename}")
            urllib.request.urlretrieve(url, filename)
            self.logger.info(f"Downloaded {filename} successfully.")
            
            # Extract the zip file to fastqc_path directory
            self.logger.info(f"Extracting {filename} to {self.fastqc_path}...")
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(self.fastqc_path)
            self.logger.info(f"Extracted {filename} successfully.")
            
            # Clean up the downloaded archive
            os.remove(filename)
            self.logger.info(f"Cleaned up {filename}.")

            # Chmod +x the FastQC executable
            os.chmod(os.path.join(self.fastqc_path, "FastQC/fastqc"), 0o755)
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error downloading or extracting FastQC: {e}")
            # Clean up partial download if it exists
            if os.path.exists(filename):
                os.remove(filename)
            return False

    def download_and_extract_corretto_jdk(self):
        """
        Detects if running on Linux x64 and downloads/extracts Amazon Corretto JDK to download directory
        """
        # Check if running on Linux
        if platform.system() != 'Linux':
            self.logger.info(f"Not running on Linux (detected: {platform.system()}). Skipping JDK download.")
            return False
        
        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ['x86_64', 'amd64']:
            self.logger.info(f"Not running on x64 architecture (detected: {machine}). Skipping JDK download.")
            return False
        
        self.logger.info("Detected Linux x64. Downloading Amazon Corretto JDK...")
        
        # URL and local filename (download to download directory)
        url = "https://corretto.aws/downloads/latest/amazon-corretto-21-x64-linux-jdk.tar.gz"
        filename = os.path.join(self.download_dir, "amazon-corretto-21-x64-linux-jdk.tar.gz")
        
        # Check if JDK already exists
        if os.path.exists(self.jdk_path):
            self.logger.info(f"Amazon Corretto JDK already exists at: {self.jdk_path}")
            return True
        
        try:
            # Download the file
            self.logger.info(f"Downloading from {url}...")
            self.logger.info(f"Saving to: {filename}")
            urllib.request.urlretrieve(url, filename)
            self.logger.info(f"Downloaded {filename} successfully.")
            
            # Extract the tar.gz file to jdk_path directory
            self.logger.info(f"Extracting {filename} to {self.jdk_path}...")
            with tarfile.open(filename, 'r:gz') as tar:
                tar.extractall(path=self.jdk_path)
            self.logger.info(f"Extracted {filename} successfully.")

            # Get the first directory in jdk_path
            self.logger.info(f"Listing contents of {self.jdk_path}:")
            contents = os.listdir(self.jdk_path)
            directories = [item for item in contents if os.path.isdir(os.path.join(self.jdk_path, item))]
            if directories:
                first_dir = directories[0]
            else:
                raise Exception("No directories found in JDK extraction")

            # Move all content from child dir first_dir to jdk_path
            for file in os.listdir(os.path.join(self.jdk_path, first_dir)):
                shutil.move(os.path.join(self.jdk_path, first_dir, file), self.jdk_path)

            # Clean up the downloaded archive
            os.remove(filename)
            self.logger.info(f"Cleaned up {filename}.")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error downloading or extracting JDK: {e}")
            # Clean up partial download if it exists
            if os.path.exists(filename):
                os.remove(filename)
            return False
