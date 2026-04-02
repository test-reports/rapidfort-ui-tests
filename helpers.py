import re


def contains(text: str) -> re.Pattern:
    """Matcher for Playwright expect(): checks if value contains the given text."""
    return re.compile(re.escape(text))
