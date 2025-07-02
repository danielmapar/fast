import os
import logging

def setup_logger():
    """Get the appropriate log file path for the user"""
    
    log_dir = os.path.expanduser(os.getenv('LOG_DIR', '~/.fast-app-logs'))
    log_file = os.path.join(log_dir, os.getenv('LOG_FILE', 'fast-app-execution.log'))
    # Remove the log file if it exists
    if os.path.exists(log_file):
        os.remove(log_file)
    # Create the log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.write('') 

    logging.basicConfig(
        level=os.getenv('LOG_LEVEL', 'INFO'),
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )