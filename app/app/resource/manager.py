import os
import sys

from PIL import Image


class ResourceManager:
    @staticmethod
    def get_resource_path(relative_path: str) -> str:
        """Get absolute path to resource, works for dev and for PyInstaller"""
        if hasattr(sys, "_MEIPASS"):
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        else:
            # Running in development
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    @staticmethod
    def open_image(relative_path: str) -> Image.Image:
        """Open image from resource path"""
        image_path = ResourceManager.get_resource_path(relative_path)
        image = Image.open(image_path)
        return image
