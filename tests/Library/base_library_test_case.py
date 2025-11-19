import os
from abc import ABC

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class BaseLibraryTestCase(ABC):
    TIMEOUT = 5
    URLS = {
        'home': 'https://biblioteka.wsiz.edu.pl/integro/catalog',
        'login': 'https://biblioteka.wsiz.edu.pl/integro/authorization/login',
        'logout': 'https://biblioteka.wsiz.edu.pl/integro/authorization/logout',
        'azure_login': 'https://biblioteka.wsiz.edu.pl/integro/authorization/azuresigin',
        'dashboard': 'https://biblioteka.wsiz.edu.pl/integro/authorization/userAttention',
        'captcha': 'https://biblioteka.wsiz.edu.pl/integro/authorization/captcha',
        'book_listing': 'https://biblioteka.wsiz.edu.pl/integro/search/description',
        'reader_card': 'https://biblioteka.wsiz.edu.pl/integro/barcode/usercard',
        'bookshelf': 'https://biblioteka.wsiz.edu.pl/integro/bookshelf',
        'book_page': 'https://biblioteka.wsiz.edu.pl/integro/{book_id}',
    }

    CREDENTIALS = {}

    def setup_method(self) -> None:
        self.CREDENTIALS.update({
            'login': os.getenv('STUDENT_LOGIN'),
            'password': os.getenv('STUDENT_PASSWORD'),
            'azure_login': os.getenv('STUDENT_AZURE_LOGIN'),
            'azure_password': os.getenv('STUDENT_AZURE_PASSWORD'),
        })

    def wait_for_cookie(self, driver, name, timeout=5):
        return WebDriverWait(driver, timeout).until(lambda d: d.get_cookie(name) is not None)

    def is_user_logged_in(self, driver) -> bool:
        try:
            return (self.wait_for_cookie(driver, '_wcagAccessKey') is not None
                    and self.wait_for_cookie(driver, 'IntegroSESSID') is not None)
        except TimeoutException:
            return False

    def wait_for_captcha_to_be_filled_if_present(self, driver):
        try:
            WebDriverWait(driver, self.TIMEOUT / 2) \
                .until(EC.presence_of_element_located((By.ID, 'LoginForm_verifyCode')))

            WebDriverWait(driver, self.TIMEOUT * 30).until(EC.url_to_be(self.URLS.get('dashboard')))

        except TimeoutException:
            pass

    def login_user(self, driver):
        driver.get(self.URLS.get('login'))

        WebDriverWait(driver, 10) \
            .until(EC.presence_of_element_located((By.ID, "LoginForm_username"))) \
            .send_keys(self.CREDENTIALS.get('login'))

        WebDriverWait(driver, 10) \
            .until(EC.presence_of_element_located((By.ID, "LoginForm_password"))) \
            .send_keys(self.CREDENTIALS.get('password'))

        WebDriverWait(driver, 10) \
            .until(EC.presence_of_element_located((By.ID, "login-form"))) \
            .submit()

        self.wait_for_captcha_to_be_filled_if_present(driver)

        self.is_user_logged_in(driver)
