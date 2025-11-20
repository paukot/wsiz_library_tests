from time import sleep

import pytest
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from tests.base_library_test_case import BaseLibraryTestCase


class TestLibraryAuthorization(BaseLibraryTestCase):
    CATALOG_SEARCH_FIELDS = {
        'search': 'SimpleSearchForm_q',
        'indexSelectBtn': 'indexChooserButton',
        'indexModal': 'indexChooser',
        'index_input': 'SimpleSearchForm_index',
        'index_button_label': 'indexChooserLabel',
        'scopeSelectBtn': 'scopeChooserButton',
        'scopeModal': 'scopeChooser',
        'scope_input': 'SimpleSearchForm_scope',
        'scope_button_label': 'scopeChooserLabel',
        'submit_button': 'submit_button',
    }

    CATALOG_HOME_FIELDS = {
        'books_listings': 'siteContentMine',
    }

    INDEX_OPTIONS = {
        'all': 1,
        'title': 2,
        'author': 3,
        'subject': 4,
    }

    SCOPE_OPTIONS = [
        'full',
        'precise',
    ]

    def get_catalog_search_url(self, search_term, search_index, search_scope):
        return f"{self.URLS.get('book_listing')}?q={search_term}&index={search_index}&scope={search_scope}"

    @pytest.mark.parametrize('search_term', ['The American Journal of Sociology'])
    def test_user_can_fill_search_terms(self, driver, search_term):
        driver.get(self.URLS.get('home'))

        search_input = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.presence_of_element_located((By.ID, self.CATALOG_SEARCH_FIELDS.get('search'))))
        search_input.send_keys(search_term)
        search_input_value = search_input.get_attribute('value')

        assert search_term in search_input_value, 'Search term was not put correctly'

    @pytest.mark.parametrize('search_index', INDEX_OPTIONS.keys())
    def test_user_can_change_index_selection(self, driver, search_index):
        driver.get(self.URLS.get('home'))

        search_index = self.INDEX_OPTIONS.get(search_index)

        index_select_button = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.ID, self.CATALOG_SEARCH_FIELDS.get('indexSelectBtn'))))
        index_select_button.click()

        index_css_selector = f"#{self.CATALOG_SEARCH_FIELDS.get('indexModal')} .simpleindex-item[data-id='{search_index}']"
        index_option = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR, index_css_selector)))
        index_option.click()

        index_input_value = driver.find_element(By.ID, self.CATALOG_SEARCH_FIELDS.get('index_input')).get_attribute(
            'value')
        index_option_label = index_option.get_attribute('data-name').strip()
        index_button_label = driver.find_element(By.ID, self.CATALOG_SEARCH_FIELDS.get('index_button_label')) \
            .get_attribute('innerHTML').strip()

        assert search_index == int(index_input_value), 'Index was not put correctly'
        assert index_button_label in index_option_label, 'Index button label was not updated correctly'

    @pytest.mark.parametrize('search_scope', SCOPE_OPTIONS)
    def test_user_can_change_scope_selection(self, driver, search_scope):
        driver.get(self.URLS.get('home'))

        scope_select_button = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.ID, self.CATALOG_SEARCH_FIELDS.get('scopeSelectBtn'))))
        scope_select_button.click()

        scope_css_selector = f"#{self.CATALOG_SEARCH_FIELDS.get('scopeModal')} .simplescope-item[data-id='{search_scope}']"
        scope_option = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR, scope_css_selector)))
        scope_option.click()

        scope_input_value = driver.find_element(By.ID, self.CATALOG_SEARCH_FIELDS.get('scope_input')).get_attribute(
            'value')
        scope_option_label = scope_option.get_attribute('data-name').strip()
        scope_button_label = driver.find_element(By.ID, self.CATALOG_SEARCH_FIELDS.get('scope_button_label')) \
            .get_attribute('innerHTML').strip()

        assert search_scope == scope_input_value, 'Scope was not put correctly'
        assert scope_button_label in scope_option_label, 'Scope button label was not updated correctly'

    @pytest.mark.parametrize('search_term,search_index,search_scope,book_id', [
        ('TDD', 'all', 'full', 422500253371),
        ('The American Journal of Sociology', 'title', 'full', 423500818836),
        ('Burzyński, Krzysztof (przedsiębiorca)', 'author', 'full', 423200610596),
        ('Fremdenverkehr - Internationalisierung - Aufsatzsammlung', 'subject', 'full', 422100135424),
    ])
    def test_user_can_search_for_books_through_catalog(self, driver, search_term, search_index, search_scope, book_id):
        driver.get(self.URLS.get('home'))

        search_index = self.INDEX_OPTIONS.get(search_index)

        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.presence_of_element_located((By.ID, self.CATALOG_SEARCH_FIELDS.get('search')))) \
            .send_keys(search_term)

        # Index Selection
        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.ID, self.CATALOG_SEARCH_FIELDS.get('indexSelectBtn')))) \
            .click()

        index_css_selector = f"#{self.CATALOG_SEARCH_FIELDS.get('indexModal')} .simpleindex-item[data-id='{search_index}']"
        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR, index_css_selector))) \
            .click()

        # Scope Selection
        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.ID, self.CATALOG_SEARCH_FIELDS.get('scopeSelectBtn')))) \
            .click()

        scope_css_selector = f"#{self.CATALOG_SEARCH_FIELDS.get('scopeModal')} .simplescope-item[data-id='{search_scope}']"
        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR, scope_css_selector))) \
            .click()

        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.ID, self.CATALOG_SEARCH_FIELDS.get('submit_button')))) \
            .click()

        try:
            book_css_selector = f"#{self.CATALOG_HOME_FIELDS.get('books_listings')} article[data-item-id='{book_id}']"
            book_listings = WebDriverWait(driver, self.TIMEOUT) \
                .until(EC.presence_of_element_located((By.ID, self.CATALOG_HOME_FIELDS.get('books_listings'))))
            book_article = WebDriverWait(driver, self.TIMEOUT) \
                .until(EC.presence_of_element_located((By.CSS_SELECTOR, book_css_selector)))
        except TimeoutException:
            book_article = None
            book_listings = None

        book_article_id = book_article.get_attribute('data-item-id') if book_article else None

        assert book_listings is not None, 'Book listings were not found'
        assert book_listings.is_displayed(), 'Book listings were not displayed'
        assert book_article, 'Book was not found'
        assert book_id == int(book_article_id), 'Book was not found'

    def test_user_can_search_for_a_nonexistent_book(self, driver):
        driver.get(self.get_catalog_search_url('tddsdgasgasdfad', 1, 'full'))

        try:
            book_empty_query = f"#{self.CATALOG_HOME_FIELDS.get('books_listings')} .info-empty"
            book_empty_info = WebDriverWait(driver, self.TIMEOUT) \
                .until(EC.presence_of_element_located((By.CSS_SELECTOR, book_empty_query)))
        except TimeoutException:
            book_empty_info = None

        assert book_empty_info is not None, 'Book listings were not displayed'
        assert book_empty_info.is_displayed(), 'Book listing not found message was not displayed'

    def test_user_is_redirected_to_book_information_page_after_clicking_on_a_book(self, driver):
        book_id = 422500253371
        book_article_css = f'article[data-item-id="{book_id}"]'

        driver.get(self.get_catalog_search_url('TDD', 1, 'full'))

        book_article = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.presence_of_element_located((By.CSS_SELECTOR, book_article_css)))
        book_article.find_element(By.CLASS_NAME, 'thumbnail').click()

        book_title = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.CLASS_NAME, 'item-details-title')))

        book_info_url = self.URLS.get('book_page').replace('{book_id}', str(book_id))

        assert book_info_url in driver.current_url, 'User was not redirected to book information page'
        assert book_title.is_displayed(), 'Book title was not displayed'

    def test_user_can_display_book_in_library_information(self, driver):
        book_id = 422500253371
        book_article_css = f'article[data-item-id="{book_id}"]'

        driver.get(self.get_catalog_search_url('TDD', 1, 'full'))

        info_button = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'{book_article_css} .search-result-details-btn')))
        info_button.click()

        info_modal = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, 'PinMapModal')))
        info_map = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, 'pinMapBox')))
        info_items = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, 'map-items')))

        assert info_modal.is_displayed(), 'Info modal was not displayed'
        assert info_map.is_displayed(), 'Info map was not displayed'
        assert info_items.is_displayed(), 'Info items were not displayed'

    def test_user_can_put_a_book_to_the_bookshelf(self, driver):
        book_id = 422500253371
        book_bookshelf_article_css = f'article[data-params="{book_id}"]'
        book_article_css = f'article[data-item-id="{book_id}"]'

        self.login_user(driver)

        # Ensure a book is not in the bookshelf
        driver.get(self.URLS.get('bookshelf'))

        listings_box = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.presence_of_element_located((By.ID, 'siteContentMine')))

        try:
            book_bookshelf = listings_box.find_element(By.CSS_SELECTOR, book_bookshelf_article_css)
        except NoSuchElementException:
            book_bookshelf = None

        if book_bookshelf:
            WebDriverWait(driver, self.TIMEOUT) \
                .until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'{book_bookshelf_article_css} .selectable'))) \
                .click()

            WebDriverWait(driver, self.TIMEOUT) \
                .until(EC.element_to_be_clickable((By.ID, 'action_tool_top'))) \
                .click()

            WebDriverWait(driver, self.TIMEOUT) \
                .until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.bbactionremoveitems'))) \
                .click()
            WebDriverWait(driver, self.TIMEOUT) \
                .until(EC.element_to_be_clickable((By.ID, 'tagConfirmModalYes'))) \
                .click()
            sleep(2)

        driver.get(self.get_catalog_search_url('TDD', 1, 'full'))

        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, f'{book_article_css} a.btn-add-to-bookbag[data-id="{book_id}"]'))) \
            .click()

        bookbag_modal = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.ID, 'modalBgAddOne')))

        bookbag_add_button = bookbag_modal.find_element(By.CSS_SELECTOR, 'button[data-buttonid="addOneBtn"]')
        bookbag_add_button.click()

        # wait for the notification box to appear
        notification_box = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.notifyjs-container')))
        notification_is_displayed = notification_box.is_displayed()

        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, f'{book_article_css} .action-flags li[data-bookbag-icon="bookbag-icon"]')))

        driver.get(self.URLS.get('bookshelf'))
        try:
            book = WebDriverWait(driver, self.TIMEOUT) \
                .until(EC.visibility_of_element_located((By.CSS_SELECTOR, book_bookshelf_article_css)))
        except TimeoutException:
            book = None

        assert notification_is_displayed, 'Notification was not displayed'
        assert book is not None, 'Book article was not found'
        assert book.is_displayed(), 'Book is not displayed on the bookshelf'
