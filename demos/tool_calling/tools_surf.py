import requests
from markdownify import markdownify
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as BrowserOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

br_options = BrowserOptions()
br_options.add_argument("--headless")
br_options.headless = True
ff_driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=br_options)


def get_webpage_content(url: str):
    print(f"Fetching webpage: '{url}'")

    response = requests.get(url)
    markdown_text = markdownify(response.text)

    return markdown_text


def get_webpage_with_js(url: str):
    print(f"Fetching webpage with JS: '{url}'")

    ff_driver.get(url)
    ff_driver.implicitly_wait(5)
    page_content = ff_driver.page_source
    markdown_text = markdownify(page_content)

    return markdown_text
