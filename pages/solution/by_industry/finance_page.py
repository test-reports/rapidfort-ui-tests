import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class FinancePage(BasePage):
    PATH_FRAGMENT = "finance"

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(re.compile(self.PATH_FRAGMENT, re.I))
