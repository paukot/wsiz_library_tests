import os

import pytest
import requests
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from tests.Library.base_library_test_case import BaseLibraryTestCase


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

    SCOPE_OPTIONS = {
        'full',
        'precise',
    }

    @pytest.mark.parametrize('search_term,search_index,search_scope,book_id', [
        ('TDD', 'all', 'full', 422500253371),
        ('The American Journal of Sociology', 'title', 'full', 423500818836),
        ('Burzyński, Krzysztof (przedsiębiorca)', 'author', 'full', 423200610596),
        ('Fremdenverkehr - Internationalisierung - Aufsatzsammlung', 'subject', 'full', 422100135424),
        ('sfafgasfasas', 'all', 'precise', None),
    ])
    def test_user_can_search_for_books_through_catalog(self, driver, search_term, search_index, search_scope, book_id):
        driver.get(self.URLS.get('home'))

        fields = self.CATALOG_SEARCH_FIELDS.copy()
        search_index = self.INDEX_OPTIONS.get(search_index)

        search_input = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.presence_of_element_located((By.ID, fields.get('search'))))
        search_input.send_keys(search_term)
        search_input_value = search_input.get_attribute('value')

        # Index Selection
        index_select_button = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.ID, fields.get('indexSelectBtn'))))
        index_select_button.click()

        index_css_selector = f"#{fields.get('indexModal')} .simpleindex-item[data-id='{search_index}']"
        index_option = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR, index_css_selector)))
        index_option.click()

        index_input_value = driver.find_element(By.ID, fields.get('index_input')).get_attribute('value')
        index_option_label = index_option.get_attribute('data-name').strip()
        index_button_label = driver.find_element(By.ID, fields.get('index_button_label')) \
            .get_attribute('innerHTML').strip()

        # Scope Selection
        scope_select_button = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.ID, fields.get('scopeSelectBtn'))))
        scope_select_button.click()

        scope_css_selector = f"#{fields.get('scopeModal')} .simplescope-item[data-id='{search_scope}']"
        scope_option = WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR, scope_css_selector)))
        scope_option.click()

        scope_input_value = driver.find_element(By.ID, fields.get('scope_input')).get_attribute('value')
        scope_option_label = scope_option.get_attribute('data-name').strip()
        scope_button_label = driver.find_element(By.ID, fields.get('scope_button_label')) \
            .get_attribute('innerHTML').strip()

        WebDriverWait(driver, self.TIMEOUT) \
            .until(EC.element_to_be_clickable((By.ID, fields.get('submit_button')))) \
            .click()

        try:
            book_css_selector = f"#{self.CATALOG_HOME_FIELDS.get('books_listings')} article[data-item-id='{book_id}']"
            book_article = WebDriverWait(driver, self.TIMEOUT) \
                .until(EC.presence_of_element_located((By.CSS_SELECTOR, book_css_selector)))
        except TimeoutException:
            book_article = None


        book_article_id = book_article.get_attribute('data-item-id') if book_article else None

        assert search_term in search_input_value, 'Search term was not put correctly'

        assert search_index == int(index_input_value), 'Index was not put correctly'
        assert index_button_label in index_option_label, 'Index button label was not updated correctly'

        assert search_scope == scope_input_value, 'Scope was not put correctly'
        assert scope_button_label in scope_option_label, 'Scope button label was not updated correctly'


        if book_id is not None:
            assert book_id == int(book_article_id), 'Book was not found'
        else:
            assert book_article_id is None, 'Book was found, but should not have been'

    def test_user_can_filter_book_listings(self, driver):
        driver.get(self.URLS.get('book_listing') + '?q=&index=1&scope=full')