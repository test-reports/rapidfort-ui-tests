import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class AboutUsPage(BasePage):
    PATH_FRAGMENT = "about"

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(re.compile(self.PATH_FRAGMENT, re.I))
