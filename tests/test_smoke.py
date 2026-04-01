def test_homepage_smoke_test(smoke_setup):
    home_page, response = smoke_setup

    assert response.ok
    home_page.expect_page_title_contains_rapidfort()
    home_page.expect_hero_visible()
