from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from tests.Library.base_library_test_case import BaseLibraryTestCase


class TestLibraryAuthorization(BaseLibraryTestCase):

    def test_user_can_access_reader_card(self, driver):
        self.login_user(driver)

        driver.get(self.URLS.get('reader_card'))

        user_card = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.presence_of_element_located((By.CSS_SELECTOR, ".user-card")))

        assert user_card.is_displayed(), 'User card was not displayed'
        assert driver.current_url == self.URLS.get('reader_card'), 'User did not stay on reader card page'
        assert self.is_user_logged_in(driver), 'User is not logged in'

    def test_user_can_access_reader_card_barcode_and_id(self, driver):
        self.login_user(driver)

        driver.get(self.URLS.get('reader_card'))

        user_card = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.presence_of_element_located((By.CSS_SELECTOR, ".user-card")))

        reader_barcode = user_card.find_element(By.CSS_SELECTOR, ".user-card-code.barcode")
        reader_card_id = user_card.find_element(By.CSS_SELECTOR, ".text-center:not(.code-toggle-wrapper)")
        reader_card_id_value = reader_card_id.get_attribute('innerHTML').strip()
        code_toggle_wrapper = user_card.find_element(By.CSS_SELECTOR, ".code-toggle-wrapper")
        barcode_toggle = code_toggle_wrapper.find_element(By.CSS_SELECTOR, "a[data-target='barcode']")
        barcode_toggle.click()

        assert barcode_toggle.is_displayed(), 'Barcode toggle was not displayed'
        assert reader_barcode.is_displayed(), 'Barcode was not displayed'
        assert reader_card_id.is_displayed(), 'Reader card ID was not displayed'
        assert reader_card_id_value.isdigit(), 'Reader card ID is not a number'

    def test_user_can_access_reader_card_qr_and_id(self, driver):
        self.login_user(driver)

        driver.get(self.URLS.get('reader_card'))

        user_card = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.presence_of_element_located((By.CSS_SELECTOR, ".user-card")))

        reader_qr = user_card.find_element(By.CSS_SELECTOR, ".user-card-code.qr")
        reader_card_id = user_card.find_element(By.CSS_SELECTOR, ".text-center:not(.code-toggle-wrapper)")
        reader_card_id_value = reader_card_id.get_attribute('innerHTML').strip()
        code_toggle_wrapper = user_card.find_element(By.CSS_SELECTOR, ".code-toggle-wrapper")
        qr_toggle = code_toggle_wrapper.find_element(By.CSS_SELECTOR, "a[data-target='qr']")
        qr_toggle.click()

        assert qr_toggle.is_displayed(), 'Barcode toggle was not displayed'
        assert reader_qr.is_displayed(), 'Barcode was not displayed'
        assert reader_card_id.is_displayed(), 'Reader card ID was not displayed'
        assert reader_card_id_value.isdigit(), 'Reader card ID is not a number'
