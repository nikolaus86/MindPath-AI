"""Load backend/.env before other modules read os.environ."""

from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent


def load_env() -> None:
    env_path = _BACKEND_DIR / ".env"
    if not env_path.is_file():
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(env_path, override=False)


load_env()
