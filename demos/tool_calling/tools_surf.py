import atexit

import requests
from markdownify import markdownify
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as BrowserOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

_ff_driver = None


def _get_driver():
    global _ff_driver
    if _ff_driver is None:
        br_options = BrowserOptions()
        br_options.add_argument("--headless")
        _ff_driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=br_options,
        )
        atexit.register(_ff_driver.quit)
    return _ff_driver


def get_webpage_content(url: str):
    print(f"Fetching webpage: '{url}'")

    response = requests.get(url)
    markdown_text = markdownify(response.text)

    return markdown_text


def get_webpage_with_js(url: str):
    print(f"Fetching webpage with JS: '{url}'")

    driver = _get_driver()
    driver.get(url)
    driver.implicitly_wait(5)
    page_content = driver.page_source
    markdown_text = markdownify(page_content)

    return markdown_text
