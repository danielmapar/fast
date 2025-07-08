import logging
import subprocess
import threading


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

            # Collect output for return value
            stdout_lines: list[str] = []
            stderr_lines: list[str] = []

            def read_output(pipe, output_lines, is_stderr=False):
                """Read output from pipe and log it in real-time"""
                if pipe is not None:
                    for line in iter(pipe.readline, ""):
                        line = line.rstrip()
                        if line:
                            # Log each line immediately as it comes
                            if is_stderr:
                                self.logger.error(line)
                            else:
                                self.logger.info(line)
                            output_lines.append(line)
                    pipe.close()

            # Create threads to read stdout and stderr simultaneously
            stdout_thread = threading.Thread(
                target=read_output, args=(process.stdout, stdout_lines, False)
            )
            stderr_thread = threading.Thread(
                target=read_output, args=(process.stderr, stderr_lines, True)
            )

            # Start threads
            stdout_thread.start()
            stderr_thread.start()

            # Wait for process to complete
            return_code = process.wait()

            # Wait for output threads to finish
            stdout_thread.join()
            stderr_thread.join()

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
