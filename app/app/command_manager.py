import os
from app.library_downloader import LibraryDownloader
from app.library_runner import LibraryRunner
import requests

class CommandManager:

    def __init__(self):
        self.download_dir = os.path.expanduser(os.getenv("DOWNLOAD_DIR"))
        self.jdk_path = os.path.join(self.download_dir, os.getenv("JDK_VERSION"))
        self.fastqc_path = os.path.join(self.download_dir, os.getenv("FASTQC_VERSION"))
        self.perl_path = os.path.join(self.download_dir, os.getenv("PERL_VERSION"))
        self.fastp_path = os.path.join(self.download_dir, os.getenv("FASTP_VERSION"))

        self.library_downloader = LibraryDownloader(self.download_dir, self.jdk_path, self.fastqc_path, self.perl_path, self.fastp_path)
        self.library_runner = LibraryRunner(self.jdk_path, self.fastqc_path, self.perl_path, self.fastp_path)

        if not self.are_libraries_installed() and not self.is_user_connected_to_internet():
            raise Exception("No internet connection and libraries are not installed! Please check your internet connection and try again.")

    def is_user_connected_to_internet(self):
        try:
            response = requests.get("https://www.google.com", timeout=5)
            return response.status_code == 200
        except:
            return False

    def are_libraries_installed(self):
        return len(os.listdir(self.download_dir)) != 0

    def setup_and_test_libraries(self):
        try:
            self.library_downloader.setup_all_libraries()
        except Exception as e:
            raise Exception(f"Error while setting up libraries: {e}")

        try:
            self.library_runner.test_all_libraries()
        except Exception as e:
            raise Exception(f"Error while testing library installations: {e}")