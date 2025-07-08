import os
import subprocess

from app.logger.config import Logger, LogType
from app.subprocess.manager import SubprocessManager


class LibraryRunner:
    def __init__(
        self,
        jdk_path: str,
        fastqc_path: str,
        perl_path: str,
        fastp_path: str,
        conda_path: str,
    ) -> None:

        # Binaries paths
        self._jdk_path = jdk_path
        self._fastqc_path = fastqc_path
        self._perl_path = perl_path
        self._fastp_path = fastp_path
        self._conda_path = conda_path

        # Loggers
        self._logger_testing_libraries = Logger().get_logger(LogType.TESTING_LIBRARIES)
        self._subprocess_manager: SubprocessManager = SubprocessManager(
            self._logger_testing_libraries
        )

    def test_all_libraries(self) -> bool:
        if os.environ.get("IGNORE_LIBRARY_TEST") == "true":
            return True

        self._logger_testing_libraries.info(
            "------------------------------------------"
        )
        self._logger_testing_libraries.info(
            "---------- Testing all libraries ---------"
        )
        self._logger_testing_libraries.info(
            "------------------------------------------"
        )

        if not self.test_jdk_installation():
            raise Exception("Failed to test JDK installation")
        if not self._test_fastqc_installation():
            raise Exception("Failed to test FastQC installation")
        if not self._test_perl_installation():
            raise Exception("Failed to test Perl installation")
        if not self._test_fastp_installation():
            raise Exception("Failed to test FastP installation")
        if not self._test_hybpiper_installation():
            raise Exception("Failed to test HybPiper installation")

        self._logger_testing_libraries.info(
            "-------------------------------------------------"
        )
        self._logger_testing_libraries.info(
            "------- All libraries tested successfully -------"
        )
        self._logger_testing_libraries.info(
            "-------------------------------------------------"
        )

        return True

    def _test_hybpiper_installation(self) -> bool:
        """
        Test if the HybPiper installation is working by running hybpiper --version
        """
        try:
            self._subprocess_manager.run_subprocess(
                [
                    os.path.join(self._conda_path, "bin", "conda"),
                    "run",
                    "-n",
                    "hybpiper",
                    "hybpiper",
                    "--version",
                ]
            )
            return True
        except Exception as e:
            self._logger_testing_libraries.error(
                f"Error testing HybPiper installation: {e}"
            )
            return False

    def _test_fastp_installation(self) -> bool:
        """
        Test if the FastP installation is working by running fastp -v
        """
        fastp_executable = self._fastp_path
        if not os.path.exists(fastp_executable):
            if self._logger_testing_libraries:
                self._logger_testing_libraries.error(
                    f"FastP executable not found at: {fastp_executable}"
                )
            return False

        try:
            result = subprocess.run(
                [fastp_executable, "-v"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                if self._logger_testing_libraries:
                    self._logger_testing_libraries.info(
                        "FastP test successful. Version info:"
                    )
                    self._logger_testing_libraries.info(result.stdout)
                return True
            else:
                if self._logger_testing_libraries:
                    self._logger_testing_libraries.error(
                        f"FastP test failed. Return code: {result.returncode}"
                    )
                    self._logger_testing_libraries.error(
                        f"Error output: {result.stderr}"
                    )
                return False
        except Exception as e:
            if self._logger_testing_libraries:
                self._logger_testing_libraries.error(
                    f"Error testing FastP installation: {e}"
                )
            return False

    def _test_perl_installation(self) -> bool:
        """
        Test if the Perl installation is working by running perl -v
        """
        perl_executable = os.path.join(self._perl_path, "bin", "perl")

        if not os.path.exists(perl_executable):
            if self._logger_testing_libraries:
                self._logger_testing_libraries.error(
                    f"Perl executable not found at: {perl_executable}"
                )
            return False

        try:
            result = subprocess.run(
                [perl_executable, "-v"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                if self._logger_testing_libraries:
                    self._logger_testing_libraries.info(
                        "Perl test successful. Version info:"
                    )
                    self._logger_testing_libraries.info(result.stdout)
                return True
            else:
                if self._logger_testing_libraries:
                    self._logger_testing_libraries.error(
                        f"Perl test failed. Return code: {result.returncode}"
                    )
                    self._logger_testing_libraries.error(
                        f"Error output: {result.stderr}"
                    )
                return False
        except Exception as e:
            if self._logger_testing_libraries:
                self._logger_testing_libraries.error(
                    f"Error testing Perl installation: {e}"
                )
            return False

    def _test_fastqc_installation(self) -> bool:
        """
        Test if the FastQC installation is working by running fastqc -v
        """
        fastqc_executable = os.path.join(self._fastqc_path, "FastQC", "fastqc")
        if not os.path.exists(fastqc_executable):
            if self._logger_testing_libraries:
                self._logger_testing_libraries.error(
                    f"FastQC executable not found at: {fastqc_executable}"
                )
            return False

        perl_executable = os.path.join(self._perl_path, "bin", "perl")
        if not os.path.exists(perl_executable):
            if self._logger_testing_libraries:
                self._logger_testing_libraries.error(
                    f"Perl executable not found at: {perl_executable}"
                )
            return False

        jdk_executable = os.path.join(self._jdk_path, "bin", "java")
        if not os.path.exists(jdk_executable):
            if self._logger_testing_libraries:
                self._logger_testing_libraries.error(
                    f"Java executable not found at: {jdk_executable}"
                )
            return False

        try:
            command = [
                perl_executable,
                fastqc_executable,
                "--java",
                jdk_executable,
                "-v",
            ]
            if self._logger_testing_libraries:
                self._logger_testing_libraries.info(
                    f"Running fastqc -v command: {" ".join(command)}"
                )
            # Run fastqc -v command
            result = self._subprocess_manager.run_subprocess(command)

            if result.returncode == 0:
                # Extract version info from stderr (fastqc -v outputs to stderr)
                version_output = result.stderr.strip()
                if self._logger_testing_libraries:
                    self._logger_testing_libraries.info(
                        "FastQC test successful. Version info:"
                    )
                    for line in version_output.split("\n"):
                        if line.strip():
                            self._logger_testing_libraries.info(f"  {line}")
                return True
            else:
                if self._logger_testing_libraries:
                    self._logger_testing_libraries.error(
                        f"FastQC test failed. Return code: {result.returncode}"
                    )
                    self._logger_testing_libraries.error(
                        f"Error output: {result.stderr}"
                    )
                return False
        except Exception as e:
            if self._logger_testing_libraries:
                self._logger_testing_libraries.error(
                    f"Error testing FastQC installation: {e}"
                )
            return False

    def test_jdk_installation(self) -> bool:
        """
        Test if the JDK installation is working by running java -version
        """
        java_executable = os.path.join(self._jdk_path, "bin", "java")

        # Check if java executable exists
        if not os.path.exists(java_executable):
            if self._logger_testing_libraries:
                self._logger_testing_libraries.error(
                    f"Java executable not found at: {java_executable}"
                )
            return False

        try:
            # Run java -version command
            result = self._subprocess_manager.run_subprocess(
                [java_executable, "-version"]
            )

            if result.returncode == 0:
                # Extract version info from stderr (java -version outputs to stderr)
                version_output = result.stderr.strip()
                if self._logger_testing_libraries:
                    self._logger_testing_libraries.info(
                        "JDK test successful. Version info:"
                    )
                    for line in version_output.split("\n"):
                        if line.strip():
                            self._logger_testing_libraries.info(f"  {line}")
                return True
            else:
                if self._logger_testing_libraries:
                    self._logger_testing_libraries.error(
                        f"JDK test failed. Return code: {result.returncode}"
                    )
                    self._logger_testing_libraries.error(
                        f"Error output: {result.stderr}"
                    )
                return False

        except Exception as e:
            if self._logger_testing_libraries:
                self._logger_testing_libraries.error(
                    f"Error testing JDK installation: {e}"
                )
            return False
