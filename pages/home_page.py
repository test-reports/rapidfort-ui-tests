import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class HomePage(BasePage):
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
        """
        Locator is a property to ensure it is always resolved fresh.
        Playwright locators are lazy, so using @property avoids stale references
        and works well with dynamic DOM updates.
        """
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

    def click_schedule_demo(self) -> None:
        self.schedule_demo.click()

    def click_request_access(self) -> None:
        self.request_access.click()

    def click_logo(self) -> None:
        self.logo.click()

    def expect_loaded(self) -> None:
        self.expect_page_title_contains_rapidfort()
        self.expect_hero_visible()

    def expect_returned_home(self) -> None:
        self.expect_url_contains(r"rapidfort\.com")

    def expect_schedule_demo_page_loaded(self) -> None:
        self.expect_url_contains(r"schedule-a-call")
        self.expect_heading_visible("Schedule a Demo")

    def expect_request_access_page_loaded(self) -> None:
        self.expect_url_contains(r"contact-us")
        self.expect_heading_visible("Contact")

    def go_to_login(self):
        from pages.login_page import LoginPage

        self.click_header_link("Login")
        return LoginPage(self.page)

    def go_to_community(self):
        from pages.community_page import CommunityPage

        self.click_nav_link("Community")
        return CommunityPage(self.page)

    def go_to_partners(self):
        from pages.partners_page import PartnersPage

        self.click_nav_link("Partners")
        return PartnersPage(self.page)

    def go_to_company(self):
        from pages.company.about_us_page import AboutUsPage

        self.click_nav_link("Company")
        return AboutUsPage(self.page)

    def go_to_blog(self):
        from pages.resources.blog_page import BlogPage

        self.click_nav_link("Resources")
        return BlogPage(self.page)

    def go_to_platform(self):
        from pages.platform.platform_overview import PlatformOverview

        self.click_nav_link("Platform")
        return PlatformOverview(self.page)

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

    def expect_intentional_failure_heading_visible(self) -> None:
        self.expect_heading_visible("Intentional Trace Failure")
