def test_partners_page_loaded(home_page):
    partners_page = home_page.go_to_partners()
    partners_page.expect_loaded()
