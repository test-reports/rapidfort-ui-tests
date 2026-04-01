def test_about_us_page_loaded(home_page):
    about_us_page = home_page.go_to_company()
    about_us_page.expect_loaded()
