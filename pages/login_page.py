import re

from pages.base_page import BasePage


class LoginPage(BasePage):
    LOGIN_URL = "https://us01.rapidfort.com/app/login"
    URL = "/login"
    TITLE = re.compile(r"Sign in", re.I)

    def open(self, path=None):
        self.page.goto(self.LOGIN_URL, wait_until="domcontentloaded")
        return self

    @property
    def heading(self):
        return self.page.get_by_role("heading", level=1, name="Sign in")

    @property
    def privacy_policy_link(self):
        return self.page.get_by_role("link", name="Privacy policy")

    @property
    def terms_of_use_link(self):
        return self.page.get_by_role("link", name="Terms of use")

    @property
    def need_help_link(self):
        return self.page.get_by_role("link", name="Need help?")

    @property
    def email_input(self):
        return self.page.get_by_role("textbox").first

    @property
    def next_button(self):
        return self.page.get_by_role("button", name="Next")

    @property
    def password_input(self):
        return self.page.get_by_role("textbox", name=re.compile(r"password", re.I))

    @property
    def sign_in_button(self):
        return self.page.get_by_role("button", name="Sign In")

    @property
    def show_password_button(self):
        return self.page.get_by_role("button", name="Show password")

    @property
    def forgot_password_link(self):
        return self.page.get_by_role("link", name="Forgot password?")

    @property
    def switch_user_link(self):
        return self.page.get_by_role("link", name="Switch user")

    @property
    def error_message(self):
        return self.page.locator(".toast-error, [role='alert']")

    @property
    def sidebar(self):
        return self.page.locator("nav, [class*='sidebar']").first

    def fill_email(self, email: str) -> None:
        self.email_input.fill(email)

    def click_next(self) -> None:
        self.next_button.click()

    def fill_password(self, password: str) -> None:
        self.password_input.fill(password)

    def click_sign_in(self) -> None:
        self.sign_in_button.click()

    def click_switch_user(self) -> None:
        self.switch_user_link.click()

    def submit_email(self, email: str) -> None:
        self.fill_email(email)
        self.click_next()

    def login(self, email: str, password: str) -> None:
        self.submit_email(email)
        self.password_input.wait_for(state="visible")
        self.fill_password(password)
        self.click_sign_in()
