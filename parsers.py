from bs4 import BeautifulSoup
from bs4 import Tag
from bs4 import NavigableString
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By


def getSoupResults(soup: BeautifulSoup) -> dict:
    """
    Extract article text from a BeautifulSoup object.

    Args:
        soup: BeautifulSoup object containing the HTML content

    Returns:
        dict: Dictionary containing extracted article content with structured keys
    """
    results_dict = {}

    # Try to find the main article content
    article_containers = []

    # Look for common article container elements
    for container in ['article', 'main', 'div.article', 'div.content', 'div.post']:
        if '.' in container:
            tag, class_name = container.split('.')
            found = soup.find_all(tag, class_=class_name)
        else:
            found = soup.find_all(container)

        if found:
            article_containers.extend(found)

    # If no specific article containers found, use the body
    if not article_containers:
        article_containers = [soup.body] if soup.body else [soup]

    # Process each potential article container
    for container_idx, container in enumerate(article_containers):
        # Extract headings
        for heading_idx, heading in enumerate(container.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
            if heading.get_text(strip=True):
                key = f"heading_{heading.name}_{container_idx}_{heading_idx}"
                results_dict[key] = heading.get_text(strip=True)

        # Extract paragraphs
        for p_idx, paragraph in enumerate(container.find_all('p')):
            if paragraph.get_text(strip=True):
                key = f"paragraph_{container_idx}_{p_idx}"
                results_dict[key] = paragraph.get_text(strip=True)

        # Extract lists
        for list_idx, list_elem in enumerate(container.find_all(['ul', 'ol'])):
            for item_idx, item in enumerate(list_elem.find_all('li')):
                if item.get_text(strip=True):
                    key = f"list_{list_elem.name}_{container_idx}_{list_idx}_{item_idx}"
                    results_dict[key] = item.get_text(strip=True)

    # If no structured content was found, fall back to the original method
    if not results_dict:
        for top_level_child in soup.find_all(recursive=True):
            for index, child in enumerate(top_level_child.descendants):
                if isinstance(child, NavigableString) and child.strip():
                    results_dict[f"{top_level_child.name}_{index}"] = child.strip()

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
