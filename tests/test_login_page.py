import pytest


@pytest.mark.smoke
def test_login_page_loaded(home_page):
    login_page = home_page.go_to_login()
    login_page.expect_loaded()
