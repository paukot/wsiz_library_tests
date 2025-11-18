import pytest
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options


@pytest.fixture
def driver(scope="session"):
    options = Options()
    driver = webdriver.Chrome(options)
    yield driver
    driver.quit()

@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()
