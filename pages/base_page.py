import re

from playwright.sync_api import Page, expect

from config.settings import BASE_URL


class BasePage:
    """
    BasePage provides reusable UI helpers.

    Use Playwright `expect()` instead of Python `assert` because it
    auto-waits and reduces UI flakiness.
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    # --- Navigation ---
    def goto(self, url: str) -> None:
        self.page.goto(url)

    def reload(self) -> None:
        self.page.reload()

    @property
    def nav_menu(self):
        return self.page.locator(".vf-nav-menu-new")

    @property
    def nav_area(self):
        return self.page.locator(".vf-nav-area")

    def open(self, path: str = "") -> None:
        target = BASE_URL if not path else f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}"
        self.page.goto(target, wait_until="domcontentloaded")

    # --- Page info ---
    def get_title(self) -> str:
        return self.page.title()

    def get_url(self) -> str:
        return self.page.url

    # --- Basic interactions (light wrappers only) ---
    def click(self, locator) -> None:
        locator.click()

    def fill(self, locator, text: str) -> None:
        locator.fill(text)

    def press(self, locator, key: str) -> None:
        locator.press(key)

    def nav_link(self, name: str):
        return self.nav_menu.get_by_role("link", name=re.compile(name, re.I))

    def header_link(self, name: str):
        return self.nav_area.get_by_role("link", name=re.compile(name, re.I))

    def click_nav_link(self, name: str) -> None:
        self.nav_link(name).click()

    def click_header_link(self, name: str) -> None:
        self.header_link(name).click()

    # --- Utility ---
    def wait_for_timeout(self, ms: int = 1000) -> None:
        self.page.wait_for_timeout(ms)

    def expect_text(self, locator, expected_text: str) -> None:
        expect(locator).to_contain_text(re.compile(expected_text, re.I))

    def expect_url_contains(self, value: str) -> None:
        expect(self.page).to_have_url(re.compile(value, re.I))

    def expect_h1(self, value: str) -> None:
        expect(
            self.page.get_by_role("heading", level=1, name=re.compile(value, re.I))
        ).to_be_visible()

    def expect_heading_visible(self, name: str, level: int = 1) -> None:
        expect(
            self.page.get_by_role("heading", level=level, name=re.compile(name, re.I))
        ).to_be_visible()
