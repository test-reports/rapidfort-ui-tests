import pytest


@pytest.mark.smoke
def test_platform_overview_loaded(home_page):
    platform_overview = home_page.go_to_platform()
    platform_overview.expect_loaded()
