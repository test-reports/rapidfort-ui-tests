import os
import sys

from dotenv import load_dotenv

load_dotenv()

DEFAULT_BASE_URL = os.getenv("BASE_URL", "https://rapidfort.com")
ENV_BASE_URLS = {
    "dev": os.getenv("BASE_URL_DEV", DEFAULT_BASE_URL),
    "qa": os.getenv("BASE_URL_QA", DEFAULT_BASE_URL),
    "staging": os.getenv("BASE_URL_STAGING", DEFAULT_BASE_URL),
}


def _cli_env_value() -> str | None:
    for i, arg in enumerate(sys.argv):
        if arg == "--env" and i + 1 < len(sys.argv):
            return sys.argv[i + 1].strip().lower()
        if arg.startswith("--env="):
            return arg.split("=", 1)[1].strip().lower()
    return None


def _resolve_target_env() -> str:
    env_name = os.getenv("TEST_ENV", "").strip().lower() or (_cli_env_value() or "")
    return env_name if env_name in ENV_BASE_URLS else ""


TARGET_ENV = _resolve_target_env()
BASE_URL = ENV_BASE_URLS.get(TARGET_ENV, DEFAULT_BASE_URL)
BROWSER = os.getenv("BROWSER", "chromium")
LOGIN_EMAIL = os.getenv("LOGIN_EMAIL", "valid@email.com")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "Password123!")