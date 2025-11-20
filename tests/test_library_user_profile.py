from time import sleep

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from tests.base_library_test_case import BaseLibraryTestCase


class TestLibraryAuthorization(BaseLibraryTestCase):
    def wait_for_bookshelf_site_to_load(self, driver):
        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.invisibility_of_element((By.CLASS_NAME, 'tag-item-blank')))
        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.tag-list .tag-item')))
        sleep(1)

    def find_bookmark_label(self, driver, label):
        label_list = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'tag-item')))

        for tag in label_list:
            label_name = tag.find_element(By.CLASS_NAME, 'tag-name')

            # expected element <span>label</span>
            if f'>{label}<' in label_name.get_attribute('innerHTML'):
                return tag
        return None

    def create_bookmark_tag_label(self, driver, label):
        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.ID, 'add-tag-btn'))) \
            .click()

        modal = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, 'tagModal')))

        modal.find_element(By.ID, 'tag-input').send_keys(label)
        modal.find_element(By.ID, 'tagModalSave').click()

        WebDriverWait(driver, self.TIMEOUT).until(EC.invisibility_of_element(modal))

        sleep(1)

        return self.find_bookmark_label(driver, label)

    def remove_tags(self, driver, tag_labels):
        if tag_labels is None:
            return

        for tag_label in tag_labels:
            tag = self.find_bookmark_label(driver, tag_label)

            if tag is None:
                continue

            tag.find_element(By.CLASS_NAME, 'tag-remove').click()

            modal = WebDriverWait(driver, self.TIMEOUT) \
                .until(EC.visibility_of_element_located((By.ID, 'tagConfirmModal')))
            modal.find_element(By.ID, 'tagConfirmModalYes').click()

            WebDriverWait(driver, self.TIMEOUT).until(EC.invisibility_of_element(modal))
            WebDriverWait(driver, self.TIMEOUT).until(EC.element_to_be_clickable((By.CLASS_NAME, 'tag-name')))
            sleep(2)

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

    def test_unauthorized_user_cannot_access_reader_card(self, driver):
        self.logout_user(driver)

        driver.get(self.URLS.get('reader_card'))

        try:
            login_form = WebDriverWait(driver, self.TIMEOUT) \
                .until(EC.visibility_of_element_located((By.ID, 'login-form')))
        except TimeoutException:
            login_form = None

        assert login_form is not None, 'Login form does not exist'
        assert driver.current_url in self.URLS.get('login'), 'User was not redirected to login page'

    def test_user_is_prompted_to_enter_password_to_access_personal_details(self, driver):
        self.login_user(driver)

        driver.get(self.URLS.get('userdata'))

        form = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, 'authentication-form')))
        password_input = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, "AuthenticationForm_password")))

        assert form.is_displayed(), 'Authentication form was not displayed'
        assert password_input.is_displayed(), 'Password input was not displayed'
        assert driver.current_url in self.URLS.get('userdata_prompt'), 'User did not stay on personal details page'
        assert self.is_user_logged_in(driver), 'User is not logged in'

    def test_user_cannot_access_personal_details_with_wrong_password(self, driver):
        self.login_user(driver)

        driver.get(self.URLS.get('userdata'))

        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, "AuthenticationForm_password"))) \
            .send_keys('WRONG PASSWORD TEST')

        driver.find_element(By.ID, 'authentication-form').submit()

        try:
            alert = WebDriverWait(driver, self.TIMEOUT) \
                .until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#userContent .alert-danger')))
        except TimeoutException:
            alert = None

        assert alert is not None, 'Alert does not exist'
        assert alert.is_displayed(), 'Alert was not displayed'
        assert driver.current_url in self.URLS.get('userdata_prompt'), 'User did not stay on personal details page'
        assert self.is_user_logged_in(driver), 'User is not logged in'

    def test_unauthorized_user_cannot_access_personal_details(self, driver):
        self.logout_user(driver)

        driver.get(self.URLS.get('userdata'))

        try:
            login_form = WebDriverWait(driver, self.TIMEOUT) \
                .until(EC.visibility_of_element_located((By.ID, 'login-form')))
        except TimeoutException:
            login_form = None

        assert login_form is not None, 'Login form does not exist'
        assert login_form.is_displayed(), 'Login form was not displayed'
        assert driver.current_url in self.URLS.get('login'), 'User was not redirected to login page'
        assert not self.is_user_logged_in(driver), 'User authentication cookies found'

    def test_user_can_access_personal_details(self, driver):
        self.login_user(driver)

        driver.get(self.URLS.get('userdata'))

        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, "AuthenticationForm_password"))) \
            .send_keys(self.CREDENTIALS.get('password'))

        driver.find_element(By.ID, 'authentication-form').submit()

        details = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#userContent .info-line')))

        assert driver.current_url in self.URLS.get('userdata'), 'User did not stay on personal details page'
        assert self.is_user_logged_in(driver), 'User is not logged in'
        assert details.is_displayed(), 'Personal details were not displayed'

    def test_user_can_access_bookshelf(self, driver):
        self.login_user(driver)

        driver.get(self.URLS.get('bookshelf'))
        self.wait_for_bookshelf_site_to_load(driver)

        title = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.presence_of_element_located((By.CLASS_NAME, 'item-details-title')))

        assert title.is_displayed(), 'Book title was not displayed'
        assert self.is_user_logged_in(driver), 'User is not logged in'
        assert driver.current_url in self.URLS.get('bookshelf'), 'User did not stay on bookshelf page'

    def test_user_can_add_a_bookshelf_tag(self, driver):
        bookmark_label = 'test_bookmark_label'
        self.login_user(driver)

        driver.get(self.URLS.get('bookshelf'))
        self.wait_for_bookshelf_site_to_load(driver)

        tag = self.create_bookmark_tag_label(driver, bookmark_label)

        assert self.is_user_logged_in(driver), 'User is not logged in'
        assert tag is not None, 'Tag was not added'
        assert tag.is_displayed(), 'Tag was not displayed'
        assert bookmark_label in tag.find_element(By.CLASS_NAME, 'tag-name').get_attribute('innerHTML'), \
            'Tag label is not correct'

    def test_user_can_change_a_bookshelf_tag_name(self, driver):
        bookmark_label = 'test_bookmark_label'
        bookmark_label_new = 'test_bookmark_label_new'

        self.login_user(driver)

        driver.get(self.URLS.get('bookshelf'))
        self.wait_for_bookshelf_site_to_load(driver)

        self.remove_tags(driver, [bookmark_label, bookmark_label_new])

        tag = self.create_bookmark_tag_label(driver, bookmark_label)
        tag.find_element(By.CLASS_NAME, 'tag-edit').click()

        modal = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, 'tagModal')))

        label_input = modal.find_element(By.ID, 'tag-input')
        label_input.clear()
        label_input.send_keys(bookmark_label_new)

        modal.find_element(By.ID, 'tagModalSave').click()

        WebDriverWait(driver, self.TIMEOUT).until(EC.invisibility_of_element(modal))
        WebDriverWait(driver, self.TIMEOUT).until(EC.element_to_be_clickable((By.CLASS_NAME, 'tag-name')))

        sleep(2)

        assert self.is_user_logged_in(driver), 'User is not logged in'
        assert self.find_bookmark_label(driver, bookmark_label) is None, 'Old tag name still exists'
        assert self.find_bookmark_label(driver, bookmark_label_new) is not None, 'New tag name does not exist'

    def test_user_can_remove_a_bookshelf_tag(self, driver):
        bookmark_label = 'test_bookmark_label'
        self.login_user(driver)

        driver.get(self.URLS.get('bookshelf'))

        self.wait_for_bookshelf_site_to_load(driver)

        self.remove_tags(driver, bookmark_label)

        assert self.is_user_logged_in(driver), 'User is not logged in'
        assert self.find_bookmark_label(driver, bookmark_label) is None, 'Tag was not removed'

    def test_user_can_filter_books_by_bookshelf_tag(self, driver):
        bookmark_label = 'test_bookmark_label'
        self.login_user(driver)

        driver.get(self.URLS.get('bookshelf'))
        self.wait_for_bookshelf_site_to_load(driver)

        tag = self.create_bookmark_tag_label(driver, bookmark_label)

        tag_id = tag.get_attribute('data-id')
        tag_url = tag.get_attribute('data-url')

        tag.click()

        self.wait_for_bookshelf_site_to_load(driver)

        assert self.is_user_logged_in(driver), 'User is not logged in'
        assert tag_id in driver.current_url, 'Tag ID was not found in URL'
        assert driver.current_url == tag_url, 'User was not properly redirected to filtered by tag page'



