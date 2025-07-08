import os
from typing import Optional

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
