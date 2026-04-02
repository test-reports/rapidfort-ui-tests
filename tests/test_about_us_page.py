from pages.company.about_us_page import AboutUsPage


def test_about_us_page_loaded(page):
    about_us_page = AboutUsPage(page).open()
    about_us_page.expect_loaded()
