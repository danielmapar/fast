import os
import sys

from PIL import Image


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Running in development
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def open_image(relative_path):
    """Open image from resource path"""
    image_path = get_resource_path(relative_path)
    print("image_path")
    print(image_path)
    image = Image.open(image_path)
    return image
