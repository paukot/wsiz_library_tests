import os

import pytest
import requests
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from tests.base_library_test_case import BaseLibraryTestCase


class TestLibraryAuthorization(BaseLibraryTestCase):
    AUTH_FIELDS = {
        'form': 'login-form',
        'login': 'LoginForm_username',
        'password': 'LoginForm_password',
        'captcha': 'getNewCode',
        'captcha_refresh': 'getNewCode_button',
        'captcha_input': 'LoginForm_verifyCode',
    }

    def element_send_keys_and_get_value(self, driver, element, value):
        el = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, element)))
        el.send_keys(value)
        return el.get_attribute('value')

    def test_user_can_log_in(self, driver):
        self.logout_user(driver)
        driver.get(self.URLS.get('login'))

        expected_login = self.CREDENTIALS.get('login')
        expected_password = self.CREDENTIALS.get('password')

        login_value = self.element_send_keys_and_get_value(driver, self.AUTH_FIELDS.get('login'), expected_login)
        password_value = self.element_send_keys_and_get_value(driver, self.AUTH_FIELDS.get('password'),
                                                              expected_password)

        driver.find_element(By.CSS_SELECTOR, f"#{self.AUTH_FIELDS.get('form')} input[type='submit']").click()

        self.wait_for_captcha_to_be_filled_if_present(driver)

        assert login_value == expected_login, 'Login value was not put correctly'
        assert password_value == expected_password, 'Password value was not put correctly'
        assert self.URLS.get('dashboard') in driver.current_url, 'User was not redirected to dashboard'
        assert self.is_user_logged_in(driver), 'User authentication cookies were not found'

    @pytest.mark.parametrize(
        'expected_login,expected_password',
        [
            ('STUDENT_LOGIN', 'wrongpasswordexample'),
            ('wronglogin123', 'STUDENT_PASSWORD'),
            ('wronglogin123', 'wrongpasswordexample'),
        ]
    )
    def test_user_cannot_log_in_with_wrong_credentials(self, driver, expected_login, expected_password):
        self.logout_user(driver)
        driver.get(self.URLS.get('login'))

        expected_login = os.getenv(expected_login, expected_login)
        expected_password = os.getenv(expected_password, expected_password)
        expected_alert = 'Niepoprawny numer karty lub hasło. Spróbuj jeszcze raz.'

        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, self.AUTH_FIELDS.get('login'))))

        login_value = self.element_send_keys_and_get_value(driver, self.AUTH_FIELDS.get('login'), expected_login)
        password_value = self.element_send_keys_and_get_value(driver, self.AUTH_FIELDS.get('password'),
                                                              expected_password)

        driver.find_element(By.CSS_SELECTOR, f"#{self.AUTH_FIELDS.get('form')} input[type='submit']").click()

        alert = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#login-form .alert.alert-danger')))

        assert login_value == expected_login, 'Login value was not put correctly'
        assert password_value == expected_password, 'Password value was not put correctly'
        assert alert.get_attribute('innerHTML') in expected_alert, 'Expected alert message was not given'
        assert self.URLS.get('login') in driver.current_url, 'User did not stay on login page'
        assert not self.is_user_logged_in(driver), 'User authentication cookies found'

    def test_user_can_log_out(self, driver):
        self.login_user(driver)

        user_logged_in_before_logout = self.is_user_logged_in(driver)

        driver.get(self.URLS.get('logout'))

        assert user_logged_in_before_logout, 'User was not logged in before logout'
        assert self.URLS.get('home') in driver.current_url, 'User was not redirected to home page'
        assert not self.is_user_logged_in(driver), 'User authentication cookies found'

    def test_user_is_prompted_to_enter_captcha_after_repeated_failed_logins(self, driver):
        self.logout_user(driver)
        driver.get(self.URLS.get('login'))

        self.element_send_keys_and_get_value(driver, self.AUTH_FIELDS.get('login'), 'test123')
        self.element_send_keys_and_get_value(driver, self.AUTH_FIELDS.get('password'), 'test123')

        for _ in range(3):
            driver.find_element(By.CSS_SELECTOR, f"#{self.AUTH_FIELDS.get('form')} input[type='submit']") \
                .click()

            try:
                WebDriverWait(driver, 1) \
                    .until(EC.visibility_of_element_located((By.ID, self.AUTH_FIELDS.get('captcha'))))
                break
            except TimeoutException:
                pass

        captcha_input = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, self.AUTH_FIELDS.get('captcha_input'))))
        captcha_img = driver.find_element(By.ID, self.AUTH_FIELDS.get('captcha'))
        first_captcha_img_is_loaded = captcha_img.is_displayed()
        first_captcha_img_url = captcha_img.get_attribute('src')
        captcha_refresh = driver.find_element(By.ID, self.AUTH_FIELDS.get('captcha_refresh'))

        captcha_refresh.click()
        try:
            WebDriverWait(driver, self.TIMEOUT) \
                .until(
                lambda d: d.find_element(By.ID, self.AUTH_FIELDS.get('captcha')) \
                              .get_attribute('src') != first_captcha_img_url
            )
        except TimeoutException:
            pass

        captcha_img = driver.find_element(By.ID, self.AUTH_FIELDS.get('captcha'))
        second_captcha_img_is_loaded = captcha_img.is_displayed()
        second_captcha_img_url = captcha_img.get_attribute('src')

        assert captcha_input, 'Captcha input was not found'
        assert first_captcha_img_is_loaded, 'Captcha image was not loaded correctly'
        assert second_captcha_img_is_loaded, 'Captcha image was not loaded correctly'
        assert first_captcha_img_url != second_captcha_img_url, 'Captcha image was not refreshed'

    def test_captcha_is_generated(self, driver):
        headers = {
            'Accept': 'application/json',
            'User-Agent': driver.execute_script("return navigator.userAgent;"),
        }

        response = requests.get(self.URLS.get('captcha'), headers=headers)

        assert response.status_code == 200
        assert response.content.startswith(b'\x89PNG'), "Captcha is not a valid PNG image"
