import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://rapidfort.com")
BROWSER = os.getenv("BROWSER", "chromium")
LOGIN_EMAIL = os.getenv("LOGIN_EMAIL", "valid@email.com")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "Password123!")