from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
HTML_DIR = REPORTS_DIR / "html"
JUNIT_DIR = REPORTS_DIR / "junit"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
TRACES_DIR = REPORTS_DIR / "traces"
SITE_DIR = PROJECT_ROOT / "site"
