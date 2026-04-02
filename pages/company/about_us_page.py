from pages.base_page import BasePage


class AboutUsPage(BasePage):
    PATH = "about"
    URL = "/about"

    def expect_loaded(self) -> None:
        self.expect_url_contains(self.URL)
