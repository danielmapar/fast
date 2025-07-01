import platform
import urllib.request
import tarfile
import os
import shutil
import zipfile
from app.library_runner import LibraryRunner

class LibraryDownloader:
    def __init__(self, download_dir, jdk_path, fastqc_path, perl_path, remove_existing_files=True):
        # Create download directory if it doesn't exist
        self.download_dir = download_dir
        print(f"Creating download directory at: {self.download_dir}")
        os.makedirs(self.download_dir, exist_ok=True) 

        # Remove all files inside the download directory
        if remove_existing_files:
            print(f"Removing all files inside the download directory at: {self.download_dir}")
            for file in os.listdir(download_dir):
                if os.path.isfile(os.path.join(download_dir, file)):
                    os.remove(os.path.join(download_dir, file))
                elif os.path.isdir(os.path.join(download_dir, file)):
                    shutil.rmtree(os.path.join(download_dir, file))

        self.jdk_path = jdk_path
        self.fastqc_path = fastqc_path
        self.perl_path = perl_path

    def setup_all_libraries(self) -> bool:
        if not self.download_and_extract_corretto_jdk():
            raise Exception("Failed to download and extract Amazon Corretto 21 JDK")
        if not self.download_and_extract_fastqc():
            raise Exception("Failed to download and extract FastQC")
        if not self.download_and_extract_perl():
            raise Exception("Failed to download and extract Perl")
        return True
    
    def download_and_extract_perl(self):
        """
        Detects if running on Linux x64 and downloads/extracts relocatable Perl to download directory
        """
        # Check if running on Linux
        if platform.system() != 'Linux':
            print(f"Not running on Linux (detected: {platform.system()}). Skipping Perl download.")
            return False
        
        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ['x86_64', 'amd64']:
            print(f"Not running on x64 architecture (detected: {machine}). Skipping Perl download.")
            return False
        
        print("Detected Linux x64. Downloading relocatable Perl...")
        
        # URL and local filename (download to download directory)
        url = "https://github.com/skaji/relocatable-perl/releases/latest/download/perl-linux-amd64.tar.xz"
        filename = os.path.join(self.download_dir, "perl-linux-amd64.tar.xz")
        
        # Check if Perl already exists
        if os.path.exists(self.perl_path):
            print(f"Perl already exists at: {self.perl_path}")
            return True
        
        try:
            # Download the file
            print(f"Downloading from {url}...")
            print(f"Saving to: {filename}")
            urllib.request.urlretrieve(url, filename)
            print(f"Downloaded {filename} successfully.")
            
            # Extract the tar.xz file to download directory first
            print(f"Extracting {filename}...")
            with tarfile.open(filename, 'r:xz') as tar:
                tar.extractall(path=self.download_dir)
            print(f"Extracted {filename} successfully.")
            
            # Move the extracted perl-linux-amd64 directory to perl_path
            extracted_dir = os.path.join(self.download_dir, "perl-linux-amd64")
            if os.path.exists(extracted_dir):
                print(f"Moving {extracted_dir} to {self.perl_path}...")
                shutil.move(extracted_dir, self.perl_path)
                print(f"Moved Perl to {self.perl_path} successfully.")
            else:
                raise Exception("Extracted perl-linux-amd64 directory not found")

            # Clean up the downloaded archive
            os.remove(filename)
            print(f"Cleaned up {filename}.")
            
            return True
        
        except Exception as e:
            print(f"Error downloading or extracting Perl: {e}")
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
            print(f"Not running on Linux (detected: {platform.system()}). Skipping FastQC download.")

        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ['x86_64', 'amd64']:
            print(f"Not running on x64 architecture (detected: {machine}). Skipping FastQC download.")
            return False
        
        print("Detected Linux x64. Downloading FastQC...")

        # URL and local filename (download to download directory)
        url = "https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.12.1.zip"
        filename = os.path.join(self.download_dir, "fastqc_v0.12.1.zip")
        
        # Check if FastQC already exists
        if os.path.exists(self.fastqc_path):
            print(f"FastQC already exists at: {self.fastqc_path}")
            return True
        
        try:
            # Download the file
            print(f"Downloading from {url}...")
            print(f"Saving to: {filename}")
            urllib.request.urlretrieve(url, filename)
            print(f"Downloaded {filename} successfully.")
            
            # Extract the zip file to fastqc_path directory
            print(f"Extracting {filename} to {self.fastqc_path}...")
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(self.fastqc_path)
            print(f"Extracted {filename} successfully.")
            
            # Clean up the downloaded archive
            os.remove(filename)
            print(f"Cleaned up {filename}.")

            # Chmod +x the FastQC executable
            os.chmod(os.path.join(self.fastqc_path, "FastQC/fastqc"), 0o755)
            
            return True
        
        except Exception as e:
            print(f"Error downloading or extracting FastQC: {e}")
            # Clean up partial download if it exists
            if os.path.exists(filename):
                os.remove(filename)
            return False

    def download_and_extract_corretto_jdk(self):
        """
        Detects if running on Linux x64 and downloads/extracts Amazon Corretto 21 JDK to download directory
        """
        # Check if running on Linux
        if platform.system() != 'Linux':
            print(f"Not running on Linux (detected: {platform.system()}). Skipping JDK download.")
            return False
        
        # Check if running on x64 architecture
        machine = platform.machine().lower()
        if machine not in ['x86_64', 'amd64']:
            print(f"Not running on x64 architecture (detected: {machine}). Skipping JDK download.")
            return False
        
        print("Detected Linux x64. Downloading Amazon Corretto 21 JDK...")
        
        # URL and local filename (download to download directory)
        url = "https://corretto.aws/downloads/latest/amazon-corretto-21-x64-linux-jdk.tar.gz"
        filename = os.path.join(self.download_dir, "amazon-corretto-21-x64-linux-jdk.tar.gz")
        
        # Check if JDK already exists
        if os.path.exists(self.jdk_path):
            print(f"Amazon Corretto 21 JDK already exists at: {self.jdk_path}")
            return True
        
        try:
            # Download the file
            print(f"Downloading from {url}...")
            print(f"Saving to: {filename}")
            urllib.request.urlretrieve(url, filename)
            print(f"Downloaded {filename} successfully.")
            
            # Extract the tar.gz file to jdk_path directory
            print(f"Extracting {filename} to {self.jdk_path}...")
            with tarfile.open(filename, 'r:gz') as tar:
                tar.extractall(path=self.jdk_path)
            print(f"Extracted {filename} successfully.")

            # Get the first directory in jdk_path
            print(f"Listing contents of {self.jdk_path}:")
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
            print(f"Cleaned up {filename}.")
            
            return True
            
        except Exception as e:
            print(f"Error downloading or extracting JDK: {e}")
            # Clean up partial download if it exists
            if os.path.exists(filename):
                os.remove(filename)
            return False
