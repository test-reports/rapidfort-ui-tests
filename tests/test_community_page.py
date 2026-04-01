def test_community_page_loaded(home_page):
    community_page = home_page.go_to_community()
    community_page.expect_loaded()
