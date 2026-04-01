import re

from playwright.sync_api import expect


def test_homepage_ui(home_page):
    home_page.expect_page_title_contains_rapidfort()
    home_page.expect_hero_visible()


def test_homepage_ctas(home_page):
    home_page.expect_hero_visible()
    home_page.expect_request_access_visible_and_enabled()
    home_page.expect_secondary_ctas_visible_and_enabled()


def test_dashboard_failure_example(home_page):
    home_page.expect_page_title_contains_rapidfort()
    expect(
        home_page.page.get_by_role(
            "heading",
            level=1,
            name=re.compile(r"Intentional Trace Failure", re.I),
        )
    ).to_be_visible()
