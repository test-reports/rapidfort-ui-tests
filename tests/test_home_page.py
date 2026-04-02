import pytest
from playwright.sync_api import expect

from helpers import contains
from pages.community_page import CommunityPage
from pages.company.about_us_page import AboutUsPage
from pages.demo_page import DemoPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.partners_page import PartnersPage
from pages.platform.platform_overview import PlatformOverview
from pages.request_access_page import RequestAccessPage
from pages.resources.blog_page import BlogPage


@pytest.mark.smoke
def test_homepage_loads(page):
    home_page = HomePage(page).open()
    expect(page).to_have_title(contains(HomePage.TITLE))
    expect(home_page.hero_heading).to_be_visible()

@pytest.mark.regression
def test_hero_ctas_visible(page):
    home_page = HomePage(page).open()
    expect(home_page.request_access).to_be_visible()
    expect(home_page.curated_images).to_be_visible()
    expect(home_page.schedule_demo).to_be_visible()

@pytest.mark.regression
def test_key_content_sections_visible(page):
    home_page = HomePage(page).open()
    expect(home_page.stats_section).to_be_visible()
    expect(home_page.faq_section).to_be_visible()
    expect(home_page.footer).to_be_visible()

@pytest.mark.regression
def test_footer_links_visible(page):
    home_page = HomePage(page).open()
    expect(home_page.footer_privacy_policy).to_be_visible()
    expect(home_page.footer_terms_of_use).to_be_visible()


@pytest.mark.regression
def test_logo_redirects_to_homepage(page):
    home_page = HomePage(page).open()
    home_page.click_schedule_demo()
    home_page.click_logo()
    expect(page).to_have_url(contains(HomePage.URL))


@pytest.mark.regression
def test_schedule_demo_navigation(page):
    home_page = HomePage(page).open()
    home_page.click_schedule_demo()
    expect(page).to_have_url(contains(DemoPage.URL))


@pytest.mark.smoke
def test_request_access_navigation(page):
    home_page = HomePage(page).open()
    home_page.click_request_access()
    expect(page).to_have_url(contains(RequestAccessPage.URL))
