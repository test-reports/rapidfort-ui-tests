import re

from playwright.sync_api import Page, expect

from config.settings import BASE_URL


class BasePage:
    """
    BasePage provides reusable UI helpers.

    Use Playwright `expect()` instead of Python `assert` because it
    auto-waits and reduces UI flakiness.

    Subclasses set PATH for direct-URL navigation via open().
    """

    PATH = ""

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, path: str | None = None):
        """Navigate to this page's PATH (no args) or a specific path. Returns self."""
        target_path = self.PATH if path is None else path
        url = BASE_URL if not target_path else f"{BASE_URL.rstrip('/')}/{target_path.lstrip('/')}"
        self.page.goto(url, wait_until="domcontentloaded")
        return self

    def reload(self) -> None:
        self.page.reload()

    @property
    def hamburger_button(self):
        return self.page.locator("button.vf-menu-button")

    def open_nav(self) -> None:
        """Open the hamburger navigation menu if not already expanded."""
        nav_indicator = self.page.get_by_role(
            "button", name=re.compile(r"^Platform$", re.I)
        )
        if not nav_indicator.is_visible():
            self.hamburger_button.click()
            nav_indicator.wait_for(state="visible")

    def expand_nav_dropdown(self, name: str) -> None:
        """Expand a dropdown section in the hamburger nav."""
        self.page.get_by_role(
            "button", name=re.compile(f"^{name}$", re.I)
        ).click()

    def get_title(self) -> str:
        return self.page.title()

    def get_url(self) -> str:
        return self.page.url

    def click(self, locator) -> None:
        locator.click()

    def fill(self, locator, text: str) -> None:
        locator.fill(text)

    def hover(self, locator) -> None:
        locator.hover()

    def press(self, locator, key: str) -> None:
        locator.press(key)

    def nav_link(self, name: str):
        return self.page.get_by_role("link", name=re.compile(name, re.I)).first

    def header_link(self, name: str):
        return self.page.get_by_role("link", name=re.compile(name, re.I)).first

    def click_nav_link(self, name: str) -> None:
        self.open_nav()
        self.nav_link(name).click()

    def hover_nav_link(self, name: str) -> None:
        """Open nav and expand the named dropdown (replaces hover on old desktop nav)."""
        self.open_nav()
        self.expand_nav_dropdown(name)

    def click_hover_nav_link(self, menu_name: str, item_name: str) -> None:
        self.click_dropdown_link(menu_name, item_name)

    def click_dropdown_link(self, dropdown_name: str, link_name: str) -> None:
        """Open nav, expand a dropdown, and click a link scoped to that dropdown."""
        self.open_nav()
        self.expand_nav_dropdown(dropdown_name)
        dropdown = self.page.get_by_role(
            "navigation", name=re.compile(f"^{dropdown_name}$", re.I)
        )
        dropdown.get_by_role(
            "link", name=re.compile(link_name, re.I)
        ).first.click()

    def click_header_link(self, name: str) -> None:
        self.open_nav()
        self.header_link(name).click()

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
