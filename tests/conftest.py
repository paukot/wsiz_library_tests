import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@pytest.fixture
def driver(scope="session"):
    options = Options()
    # options.add_argument('--headless')
    options.add_argument("--window-size=1240,1024")
    options.add_experimental_option("prefs", {"profile.default_content_setting_values.clipboard": 1})
    driver = webdriver.Chrome(options)
    yield driver
    driver.quit()


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()
