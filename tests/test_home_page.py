import pytest


@pytest.mark.smoke
def test_homepage_smoke(home_page):
    home_page.expect_loaded()


def test_homepage_ctas(home_page):
    home_page.expect_hero_visible()
    home_page.expect_request_access_visible_and_enabled()
    home_page.expect_secondary_ctas_visible_and_enabled()


@pytest.mark.smoke
def test_logo_redirects_to_homepage(home_page):
    home_page.click_schedule_demo()
    home_page.click_logo()
    home_page.expect_returned_home()


@pytest.mark.smoke
def test_schedule_demo_navigation(home_page):
    home_page.click_schedule_demo()
    home_page.expect_schedule_demo_page_loaded()


@pytest.mark.smoke
def test_request_access_navigation(home_page):
    home_page.click_request_access()
    home_page.expect_request_access_page_loaded()
