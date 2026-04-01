import re

from playwright.sync_api import expect


def test_logo_returns_to_homepage(home_page):
    home_page.click_schedule_demo()
    home_page.click_logo()
    expect(home_page.page).to_have_url(re.compile(r"rapidfort\.com"))


def test_schedule_demo_navigation(home_page):
    home_page.click_schedule_demo()
    expect(home_page.page).to_have_url(re.compile(r"schedule-a-call"))
    expect(
        home_page.page.get_by_role(
            "heading", level=1, name=re.compile(r"Schedule a Demo", re.I)
        )
    ).to_be_visible()


def test_request_access_navigation(home_page):
    home_page.click_request_access()
    expect(home_page.page).to_have_url(re.compile(r"contact-us"))
    expect(
        home_page.page.get_by_role("heading", level=1, name=re.compile(r"Contact", re.I))
    ).to_be_visible()
