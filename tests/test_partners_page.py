from pages.partners_page import PartnersPage


def test_partners_page_loaded(page):
    partners_page = PartnersPage(page).open()
    partners_page.expect_loaded()
