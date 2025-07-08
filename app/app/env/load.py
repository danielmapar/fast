import os
import sys

import dotenv


# Handle .env loading for PyInstaller bundles
def load_env_vars() -> None:

    if getattr(sys, "frozen", False):
        # Running in a PyInstaller bundle
        if hasattr(sys, "_MEIPASS"):
            bundle_dir = sys._MEIPASS
            env_path = os.path.join(bundle_dir, ".env")
        else:
            env_path = ".env"
    else:
        # Running in normal Python environment
        env_path = ".env"

    dotenv.load_dotenv(dotenv_path=env_path)
