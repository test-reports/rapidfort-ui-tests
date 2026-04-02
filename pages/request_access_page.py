from pages.base_page import BasePage


class RequestAccessPage(BasePage):
    PATH = "contact-us"
    URL = "/contact-us"
    H1 = "Contact"

    def expect_loaded(self) -> None:
        self.expect_url_contains(self.URL)
        self.expect_h1(self.H1)
