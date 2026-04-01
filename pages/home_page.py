import re

from playwright.sync_api import Page, expect

from config.settings import BASE_URL


class HomePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def hero_heading(self):
        return self.page.get_by_role("heading", level=1)

    @property
    def hero_section(self):
        return self.page.locator("section:has(h1)")

    @property
    def nav_menu(self):
        return self.page.locator(".vf-nav-menu-new")

    @property
    def nav_area(self):
        return self.page.locator(".vf-nav-area")

    @property
    def request_access(self):
        return self.hero_section.get_by_role("link", name="Request Access")

    @property
    def curated_images(self):
        return self.hero_section.get_by_role("link", name="Curated Images")

    @property
    def schedule_demo(self):
        return self.nav_menu.get_by_role("link", name="Schedule a Demo")

    @property
    def logo(self):
        return self.nav_area.locator("a.vf-nav-logo")

    def open(self) -> None:
        self.page.goto(BASE_URL, wait_until="domcontentloaded")

    def click_schedule_demo(self) -> None:
        self.schedule_demo.click()

    def click_request_access(self) -> None:
        self.request_access.click()

    def click_logo(self) -> None:
        self.logo.click()

    def expect_hero_visible(self) -> None:
        expect(self.hero_heading).to_be_visible()

    def expect_page_title_contains_rapidfort(self) -> None:
        expect(self.page).to_have_title(re.compile(r"RapidFort", re.I))

    def expect_request_access_visible_and_enabled(self) -> None:
        expect(self.request_access).to_be_visible()
        expect(self.request_access).to_be_enabled()

    def expect_secondary_ctas_visible_and_enabled(self) -> None:
        expect(self.schedule_demo).to_be_visible()
        expect(self.schedule_demo).to_be_enabled()
        expect(self.curated_images).to_be_visible()
        expect(self.curated_images).to_be_enabled()
