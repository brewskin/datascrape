from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By


def getSoupResults(soup: BeautifulSoup) -> dict:
    results_dict = {}
    for element in soup.find_all(recursive=True):
        child_result_dict = {}

        for index, child in enumerate(element.children):
            index_name = f"child_{index}"

            this_type = type(child)
            print(this_type)

            text = child.get_text().strip()
            if text:
                child_result_dict[index_name] = text.encode(
                    'utf-8').decode('utf-8')

        results_dict[element.name] = child_result_dict

    links_result = {}
    links = soup.find_all('a')
    for link in links:
        link_text = link.get_text()
        href = link.get('href')
        if href:
            links_result[link_text] = href

    results_dict["page_links"] = links_result

    return results_dict


class DefaultParser:
    """Default text extractor"""

    def __init__(self) -> None:
        pass

    def parse_article(self, url: str) -> dict:
        response = requests.get(url)

        try:
            soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print("Error:", e)
            return {}

        return getSoupResults(soup)


class SeleniumParser:
    """Extract text using Selenium"""

    def __init__(self) -> None:
        pass

    def parse_article(self, url: str) -> dict:
        driver = webdriver.Chrome()
        # Navigate to a web page
        driver.get(url)
        # Extract data from the rendered page
        page_source = driver.page_source
        # Close the WebDriver
        driver.quit()

        try:
            soup = BeautifulSoup(page_source, 'html.parser')
        except Exception as e:
            print("Error:", e)
            return {}

        return getSoupResults(soup)


def digIntoContent(child, child_result_dict) -> dict:
    for index, c_contents in enumerate(child.contents):
        child_result_dict[c_contents.name] = c_contents.text

    return child_result_dict


def tryGetName(item) -> str:
    name = ''
    try:
        name = item.name
    except:
        return ''

    return name


def hasContent(item) -> bool:
    try:
        content = item.content
    except:
        return False

    return True
