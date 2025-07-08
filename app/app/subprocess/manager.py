import logging
import subprocess


class SubprocessManager:
    def __init__(self, logger: logging.Logger):
        # Loggers
        self.logger = logger

    def run_subprocess(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        """Run subprocess command with real-time line-by-line logging"""
        try:
            # Start the process
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True,
            )

            # Read output line by line in real-time
            stdout_lines = []
            stderr_lines = []

            stdout, stderr = process.communicate()

            # Log stdout
            if stdout:
                for line in stdout.split("\n"):
                    if line.strip():
                        self.logger.info(line)
                        stdout_lines.append(line)

            # Log stderr
            if stderr:
                for line in stderr.split("\n"):
                    if line.strip():
                        self.logger.info(line)
                        stderr_lines.append(line)

            # Wait for process to complete and get return code
            return_code = process.returncode

            # Create and return CompletedProcess object
            return subprocess.CompletedProcess(
                args=command,
                returncode=return_code,
                stdout="\n".join(stdout_lines),
                stderr="\n".join(stderr_lines),
            )

        except Exception as e:
            self.logger.error(f"Subprocess failed: {' '.join(command)}")
            self.logger.error(f"Error: {e}")
            raise
