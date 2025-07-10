from app.app import App
from app.env.load import load_env_vars
from app.logger.config import init_logger

load_env_vars()

init_logger()


def run_app() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run_app()
