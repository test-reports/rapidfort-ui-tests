from pages.base_page import BasePage


class DemoPage(BasePage):
    PATH = "schedule-a-call"
    URL = "/schedule-a-call"
    H1 = "Schedule a Demo"

    def expect_loaded(self) -> None:
        self.expect_url_contains(self.URL)
        self.expect_h1(self.H1)
