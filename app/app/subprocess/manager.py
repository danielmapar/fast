import logging
import subprocess


class SubprocessManager:
    def __init__(self, logger: logging.Logger):
        # Loggers
        self.logger = logger

    def run_subprocess(self, command: list[str]) -> None:
        """Run subprocess command with real-time line-by-line logging"""
        try:
            # Start the process
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True,
            )

            # Read output line by line in real-time
            stdout = process.stdout
            if stdout is not None:
                while True:
                    line = stdout.readline()
                    if not line:
                        break
                    # Log each line immediately as it comes
                    self.logger.info(line.rstrip())

            # Wait for process to complete and get return code
            return_code = process.wait()

            # Check if the process succeeded
            if return_code != 0:
                raise subprocess.CalledProcessError(return_code, command)

        except Exception as e:
            self.logger.error(f"Subprocess failed: {' '.join(command)}")
            self.logger.error(f"Error: {e}")
            raise
