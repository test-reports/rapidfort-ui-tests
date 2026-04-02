from pages.base_page import BasePage


class PartnersPage(BasePage):
    PATH = "partners"
    URL = "/partners"

    def expect_loaded(self) -> None:
        self.expect_url_contains(self.URL)
