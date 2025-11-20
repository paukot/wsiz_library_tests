import os

import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


@pytest.fixture(scope="session")
def driver():
    load_dotenv()

    service = Service(executable_path=os.getenv('CHROMEDRIVER_PATH'))
    options = Options()
    # options.add_argument('--headless')
    options.add_argument("--window-size=1240,1024")

    driver = webdriver.Chrome(service=service, options=options)

    yield driver

    driver.quit()


@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()
