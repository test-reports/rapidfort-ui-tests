from pages.base_page import BasePage


class PlatformOverview(BasePage):
    PATH = "platform"
    URL = "/platform"

    def expect_loaded(self) -> None:
        self.expect_url_contains(self.URL)
