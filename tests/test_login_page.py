import json
from pathlib import Path

import pytest
from playwright.sync_api import expect

from config.settings import LOGIN_EMAIL, LOGIN_PASSWORD
from helpers import contains
from pages.login_page import LoginPage
from utils.api_helper import create_mock_user

@pytest.mark.smoke
def test_login_page_loads(page):
    login_page = LoginPage(page).open()
    expect(page).to_have_title(LoginPage.TITLE)
    expect(login_page.heading).to_be_visible()
    expect(login_page.email_input).to_be_visible()
    expect(login_page.next_button).to_be_visible()

@pytest.mark.smoke
def test_login_with_valid_credentials(page):
    login_page = LoginPage(page).open()
    login_page.login(LOGIN_EMAIL, LOGIN_PASSWORD)
    expect(page).not_to_have_url(contains(LoginPage.URL))
    expect(login_page.sidebar).to_be_visible()

@pytest.mark.smoke
def test_login_with_valid_email_invalid_password(page):
    login_page = LoginPage(page).open()
    login_page.login(LOGIN_EMAIL, "wrongpassword")
    expect(page).to_have_url(contains(LoginPage.URL))
    expect(login_page.error_message).to_be_visible()

@pytest.mark.regression
def test_login_with_nonexistent_email_and_password(page):
    login_page = LoginPage(page).open()
    login_page.login("nonexistent@fakeemail.com", "anypassword")
    expect(page).to_have_url(contains(LoginPage.URL))
    expect(login_page.error_message).to_be_visible()

@pytest.mark.regression
def test_login_with_invalid_email_format(page):
    login_page = LoginPage(page).open()
    login_page.fill_email("not-an-email")
    login_page.click_next()
    expect(login_page.password_input).not_to_be_visible()
    expect(login_page.email_input).to_be_visible()

@pytest.mark.regression
def test_login_with_empty_email(page):
    login_page = LoginPage(page).open()
    login_page.click_next()
    expect(login_page.password_input).not_to_be_visible()
    expect(login_page.email_input).to_be_visible()

@pytest.mark.regression
def test_login_with_empty_password(page):
    login_page = LoginPage(page).open()
    login_page.submit_email(LOGIN_EMAIL)
    login_page.password_input.wait_for(state="visible")
    login_page.click_sign_in()
    expect(page).to_have_url(contains(LoginPage.URL))

LOGIN_CASES_PATH = Path(__file__).parent / "testdata" / "login_cases.json"


def _load_login_cases():
    raw_cases = json.loads(LOGIN_CASES_PATH.read_text())
    cases = []
    for case in raw_cases:
        cases.append(
            pytest.param(
                case["email"],
                case["password"],
                id=case["id"],
            )
        )
    return cases

@pytest.mark.regression
@pytest.mark.parametrize(
    "email,password",
    _load_login_cases(),
)
def test_login_negative_scenarios_data_driven(page, email, password):
    login_page = LoginPage(page).open()
    login_page.login(email, password)
    expect(page).to_have_url(contains(LoginPage.URL))
    expect(login_page.error_message).to_be_visible()


@pytest.mark.regression
def test_login_ui_with_user_created_by_api_helper(page):
    login_page = LoginPage(page).open()
    user = create_mock_user(page, email="valid@user.com", password="Password123")

    login_page.login(user["email"], user["password"])
    # expect(page).not_to_have_url(contains(LoginPage.URL))
    # expect(login_page.sidebar).to_be_visible()
