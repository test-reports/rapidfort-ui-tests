from pages.base_page import BasePage


class FinancePage(BasePage):
    URL = "/finance"
    PATH = "solutions/by-industry/finance"

    def expect_loaded(self) -> None:
        self.expect_url_contains(self.URL)
