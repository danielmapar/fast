import logging
import threading


class LambdaThreadRunner(threading.Thread):
    """Custom thread class that can execute lambda functions with callbacks"""

    def __init__(self, target_function, on_success=None, on_error=None, daemon=True):
        """
        Initialize the thread

        Args:
            target_function: The lambda function or callable to execute
            on_success: Callback function to call on successful completion (optional)
            on_error: Callback function to call on error (receives exception as parameter)
            daemon: Whether this should be a daemon thread
        """
        super().__init__(daemon=daemon)
        self.target_function = target_function
        self.on_success = on_success
        self.on_error = on_error
        self.logger = logging.getLogger()

    def run(self):
        """Execute the target function and handle callbacks"""
        try:
            result = self.target_function()

            if self.on_success:
                self.on_success(result)
        except Exception as e:
            if self.on_error:
                self.on_error(e)
            else:
                self.logger.error(f"Thread error: {e}")
