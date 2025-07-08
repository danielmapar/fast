import os
import subprocess

from app.logger.config import Logger, LogType


class LibraryRunner:
    def __init__(
        self,
        jdk_path: str,
        fastqc_path: str,
        perl_path: str,
        fastp_path: str,
        conda_path: str,
    ) -> None:
        self.jdk_path = jdk_path
        self.fastqc_path = fastqc_path
        self.perl_path = perl_path
        self.fastp_path = fastp_path
        self.conda_path = conda_path
        self.logger_testing_libraries = Logger().get_logger(LogType.TESTING_LIBRARIES)

    def test_all_libraries(self) -> bool:
        if os.environ.get("IGNORE_LIBRARY_TEST") == "true":
            return True

        if self.logger_testing_libraries:
            self.logger_testing_libraries.info(
                "------------------------------------------"
            )
            self.logger_testing_libraries.info(
                "---------- Testing all libraries ---------"
            )
            self.logger_testing_libraries.info(
                "------------------------------------------"
            )

        if not self.test_jdk_installation():
            raise Exception("Failed to test JDK installation")
        if not self.test_fastqc_installation():
            raise Exception("Failed to test FastQC installation")
        if not self.test_perl_installation():
            raise Exception("Failed to test Perl installation")
        if not self.test_fastp_installation():
            raise Exception("Failed to test FastP installation")
        if not self.test_hybpiper_installation():
            raise Exception("Failed to test HybPiper installation")

        if self.logger_testing_libraries:
            self.logger_testing_libraries.info(
                "-------------------------------------------------"
            )
            self.logger_testing_libraries.info(
                "------- All libraries tested successfully -------"
            )
            self.logger_testing_libraries.info(
                "-------------------------------------------------"
            )

        return True

    def test_hybpiper_installation(self) -> bool:
        """
        Test if the HybPiper installation is working by running hybpiper --version
        """
        try:
            subprocess.run(
                [
                    os.path.join(self.conda_path, "bin", "conda"),
                    "run",
                    "-n",
                    "hybpiper",
                    "hybpiper",
                    "--version",
                ],
                check=True,
            )
            return True
        except Exception as e:
            if self.logger_testing_libraries:
                self.logger_testing_libraries.error(
                    f"Error testing HybPiper installation: {e}"
                )
            return False

    def test_fastp_installation(self) -> bool:
        """
        Test if the FastP installation is working by running fastp -v
        """
        fastp_executable = self.fastp_path
        if not os.path.exists(fastp_executable):
            if self.logger_testing_libraries:
                self.logger_testing_libraries.error(
                    f"FastP executable not found at: {fastp_executable}"
                )
            return False

        try:
            result = subprocess.run(
                [fastp_executable, "-v"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                if self.logger_testing_libraries:
                    self.logger_testing_libraries.info(
                        "FastP test successful. Version info:"
                    )
                    self.logger_testing_libraries.info(result.stdout)
                return True
            else:
                if self.logger_testing_libraries:
                    self.logger_testing_libraries.error(
                        f"FastP test failed. Return code: {result.returncode}"
                    )
                    self.logger_testing_libraries.error(
                        f"Error output: {result.stderr}"
                    )
                return False
        except Exception as e:
            if self.logger_testing_libraries:
                self.logger_testing_libraries.error(
                    f"Error testing FastP installation: {e}"
                )
            return False

    def test_perl_installation(self) -> bool:
        """
        Test if the Perl installation is working by running perl -v
        """
        perl_executable = os.path.join(self.perl_path, "bin", "perl")

        if not os.path.exists(perl_executable):
            if self.logger_testing_libraries:
                self.logger_testing_libraries.error(
                    f"Perl executable not found at: {perl_executable}"
                )
            return False

        try:
            result = subprocess.run(
                [perl_executable, "-v"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                if self.logger_testing_libraries:
                    self.logger_testing_libraries.info(
                        "Perl test successful. Version info:"
                    )
                    self.logger_testing_libraries.info(result.stdout)
                return True
            else:
                if self.logger_testing_libraries:
                    self.logger_testing_libraries.error(
                        f"Perl test failed. Return code: {result.returncode}"
                    )
                    self.logger_testing_libraries.error(
                        f"Error output: {result.stderr}"
                    )
                return False
        except Exception as e:
            if self.logger_testing_libraries:
                self.logger_testing_libraries.error(
                    f"Error testing Perl installation: {e}"
                )
            return False

    def test_fastqc_installation(self) -> bool:
        """
        Test if the FastQC installation is working by running fastqc -v
        """
        fastqc_executable = os.path.join(self.fastqc_path, "FastQC", "fastqc")
        if not os.path.exists(fastqc_executable):
            if self.logger_testing_libraries:
                self.logger_testing_libraries.error(
                    f"FastQC executable not found at: {fastqc_executable}"
                )
            return False

        perl_executable = os.path.join(self.perl_path, "bin", "perl")
        if not os.path.exists(perl_executable):
            if self.logger_testing_libraries:
                self.logger_testing_libraries.error(
                    f"Perl executable not found at: {perl_executable}"
                )
            return False

        jdk_executable = os.path.join(self.jdk_path, "bin", "java")
        if not os.path.exists(jdk_executable):
            if self.logger_testing_libraries:
                self.logger_testing_libraries.error(
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
            if self.logger_testing_libraries:
                self.logger_testing_libraries.info(
                    f"Running fastqc -v command: {" ".join(command)}"
                )
            # Run fastqc -v command
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                # Extract version info from stderr (fastqc -v outputs to stderr)
                version_output = result.stderr.strip()
                if self.logger_testing_libraries:
                    self.logger_testing_libraries.info(
                        "FastQC test successful. Version info:"
                    )
                    for line in version_output.split("\n"):
                        if line.strip():
                            self.logger_testing_libraries.info(f"  {line}")
                return True
            else:
                if self.logger_testing_libraries:
                    self.logger_testing_libraries.error(
                        f"FastQC test failed. Return code: {result.returncode}"
                    )
                    self.logger_testing_libraries.error(
                        f"Error output: {result.stderr}"
                    )
                return False
        except Exception as e:
            if self.logger_testing_libraries:
                self.logger_testing_libraries.error(
                    f"Error testing FastQC installation: {e}"
                )
            return False

    def test_jdk_installation(self) -> bool:
        """
        Test if the JDK installation is working by running java -version
        """
        java_executable = os.path.join(self.jdk_path, "bin", "java")

        # Check if java executable exists
        if not os.path.exists(java_executable):
            if self.logger_testing_libraries:
                self.logger_testing_libraries.error(
                    f"Java executable not found at: {java_executable}"
                )
            return False

        try:
            # Run java -version command
            result = subprocess.run(
                [java_executable, "-version"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                # Extract version info from stderr (java -version outputs to stderr)
                version_output = result.stderr.strip()
                if self.logger_testing_libraries:
                    self.logger_testing_libraries.info(
                        "JDK test successful. Version info:"
                    )
                    for line in version_output.split("\n"):
                        if line.strip():
                            self.logger_testing_libraries.info(f"  {line}")
                return True
            else:
                if self.logger_testing_libraries:
                    self.logger_testing_libraries.error(
                        f"JDK test failed. Return code: {result.returncode}"
                    )
                    self.logger_testing_libraries.error(
                        f"Error output: {result.stderr}"
                    )
                return False

        except subprocess.TimeoutExpired:
            if self.logger_testing_libraries:
                self.logger_testing_libraries.error(
                    "JDK test timed out after 10 seconds"
                )
            return False
        except Exception as e:
            if self.logger_testing_libraries:
                self.logger_testing_libraries.error(
                    f"Error testing JDK installation: {e}"
                )
            return False
