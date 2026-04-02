import pytest

from pages.platform.platform_overview import PlatformOverview


@pytest.mark.smoke
def test_platform_overview_loaded(page):
    platform_overview = PlatformOverview(page).open()
    platform_overview.expect_loaded()
