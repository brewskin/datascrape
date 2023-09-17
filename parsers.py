from bs4 import BeautifulSoup
from bs4 import Tag
from bs4 import NavigableString
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By


def getSoupResults(soup: BeautifulSoup) -> dict:
    results_dict = {}
    for element in soup.find_all(recursive=True):
        child_result_dict = {}

        for index, child in enumerate(element.children):
            if isinstance(child, Tag):
                if child.name == 'a':
                    continue
                print(child.name)
                child_string = child.get_text()
                if child_string is None:
                    continue
                elif child_string == '':
                    continue

                results_dict[f"{element.name}_{child.name}_{index}"] = child_string.encode(
                    'utf-8').decode('utf-8')

            elif isinstance(child, NavigableString):
                text = child.get_text().strip()
                if text:
                    results_dict[f"{element.name}_{child.name}_{index}"] = text.encode(
                        'utf-8').decode('utf-8')

    # links_result = {}
    # links = soup.find_all('a')
    # for link in links:
    #     link_text = link.get_text()
    #     href = link.get('href')
    #     if href:
    #         links_result[link_text] = href

    # results_dict["page_links"] = links_result

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
