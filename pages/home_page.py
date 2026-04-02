import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class HomePage(BasePage):
    PATH = ""
    URL = "rapidfort.com"
    TITLE = "RapidFort"
    HERO_HEADING = re.compile(r"Remediate.*CVEs", re.I)

    @property
    def hero_heading(self):
        return self.page.get_by_role("heading", level=1, name=self.HERO_HEADING)

    @property
    def request_access(self):
        return self.page.get_by_role("link", name="Request Access").first

    @property
    def curated_images(self):
        return self.page.get_by_role("link", name="Curated Images").first

    @property
    def schedule_demo(self):
        return self.page.get_by_role("link", name="Schedule a Demo").first

    @property
    def logo(self):
        return self.page.locator("a.vf-nav-logo")

    @property
    def sign_in_link(self):
        return self.page.get_by_role("link", name=re.compile(r"^Sign In$", re.I)).first

    @property
    def faq_section(self):
        return self.page.get_by_role("heading", name=re.compile(r"frequently asked questions", re.I))

    @property
    def stats_section(self):
        return self.page.locator("text=Attack Surface Reduction").first

    @property
    def footer(self):
        return self.page.get_by_text(re.compile(r"©.*RapidFort", re.I)).first

    @property
    def footer_privacy_policy(self):
        return self.page.get_by_role("link", name="Privacy Policy")

    @property
    def hero_section(self):
        return self.hero_heading.locator("xpath=ancestor::section[1]")

    @property
    def footer_terms_of_use(self):
        return self.page.get_by_role("link", name="Terms of Use")

    def click_schedule_demo(self) -> None:
        self.schedule_demo.click()

    def click_request_access(self) -> None:
        self.request_access.click()

    def click_logo(self) -> None:
        self.logo.click()

    def click_curated_images(self) -> None:
        self.curated_images.click()

    def click_sign_in(self) -> None:
        self.open_nav()
        self.sign_in_link.click()

    def click_community(self) -> None:
        self.click_nav_link("Community")

    def click_partners(self) -> None:
        self.click_nav_link("Partners")

    def click_about_us(self) -> None:
        self.click_nav_link("About Us")

    def click_rapidfort_blog(self) -> None:
        self.click_nav_link("RapidFort Blog")

    def click_platform_overview(self) -> None:
        self.click_nav_link("Platform Overview")

    def click_company(self) -> None:
        self.click_dropdown_link("Company", "About Us")

    def click_blog(self) -> None:
        self.click_dropdown_link("Resources", "RapidFort Blog")

    def click_platform(self) -> None:
        self.click_dropdown_link("Platform", "Platform Overview")

    def expect_loaded(self) -> None:
        self.expect_page_title_contains_rapidfort()
        self.expect_hero_visible()

    def expect_returned_home(self) -> None:
        self.expect_url_contains(r"rapidfort\.com")
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
