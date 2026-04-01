from pages.base_page import BasePage


class BlogPage(BasePage):
    URL = "/blog"
    H1 = "Blog"

    def expect_loaded(self) -> None:
        self.expect_url_contains(self.URL)
        self.expect_h1(self.H1)
