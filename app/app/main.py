from .app import App
from .env.load import load_env_vars
from .logger.config import setup_logger

load_env_vars()

setup_logger()


def run_app():
    app = App()
    app.mainloop()


def main():
    run_app()


if __name__ == "__main__":
    run_app()
