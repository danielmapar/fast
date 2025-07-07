import os
import sys

import dotenv


# Handle .env loading for PyInstaller bundles
def load_env_vars():

    if getattr(sys, "frozen", False):
        # Running in a PyInstaller bundle
        bundle_dir = sys._MEIPASS
        env_path = os.path.join(bundle_dir, ".env")
    else:
        # Running in normal Python environment
        env_path = ".env"

    dotenv.load_dotenv(dotenv_path=env_path)
