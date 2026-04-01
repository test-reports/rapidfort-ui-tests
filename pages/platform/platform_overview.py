import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class PlatformOverview(BasePage):
    PATH_FRAGMENT = "platform"

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(re.compile(self.PATH_FRAGMENT, re.I))
