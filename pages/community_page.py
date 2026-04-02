from pages.base_page import BasePage


class CommunityPage(BasePage):
    PATH = "community"
    URL = "/community"

    def expect_loaded(self) -> None:
        self.expect_url_contains(self.URL)
