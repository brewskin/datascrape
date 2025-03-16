from bs4 import BeautifulSoup
from bs4 import Tag
from bs4 import NavigableString
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

# Global debug log list to store debug information
debug_logs = []


def add_debug_log(message):
    """Add a debug message to the global debug logs"""
    debug_logs.append(message)
    print(f"DEBUG: {message}")


def get_debug_logs():
    """Get all debug logs as HTML formatted string"""
    if not debug_logs:
        return "<p>No debug logs recorded</p>"

    log_html = "<h3>Debug Logs:</h3><ul>"
    for log in debug_logs:
        log_html += f"<li>{log}</li>"
    log_html += "</ul>"
    return log_html


def getSoupResults(soup: BeautifulSoup) -> dict:
    """
    Extract article text from a BeautifulSoup object.

    Args:
        soup: BeautifulSoup object containing the HTML content

    Returns:
        dict: Dictionary containing extracted article content with structured keys
    """
    # Clear previous debug logs
    global debug_logs
    debug_logs = []

    add_debug_log(f"Starting HTML parsing with BeautifulSoup")

    # Debug the HTML structure
    html_preview = str(soup)[:500] + \
        "..." if len(str(soup)) > 500 else str(soup)
    add_debug_log(f"HTML preview: {html_preview}")

    results_dict = {}

    # Try to find the main article content
    article_containers = []

    # Look for common article container elements
    add_debug_log("Looking for article containers...")
    for container in ['article', 'main', 'div.article', 'div.content', 'div.post']:
        if '.' in container:
            tag, class_name = container.split('.')
            found = soup.find_all(tag, class_=class_name)
            add_debug_log(
                f"Searching for {tag} with class {class_name}: found {len(found)} elements")
        else:
            found = soup.find_all(container)
            add_debug_log(
                f"Searching for {container} tag: found {len(found)} elements")

        if found:
            article_containers.extend(found)

    add_debug_log(f"Total article containers found: {len(article_containers)}")

    # If no specific article containers found, use the body
    if not article_containers:
        add_debug_log(
            "No specific article containers found, falling back to body or entire document")
        if soup.body:
            add_debug_log("Using body tag as container")
            article_containers = [soup.body]
        else:
            add_debug_log("No body tag found, using entire document")
            article_containers = [soup]

    # Process each potential article container
    total_headings = 0
    total_paragraphs = 0
    total_list_items = 0

    for container_idx, container in enumerate(article_containers):
        add_debug_log(
            f"Processing container {container_idx+1}/{len(article_containers)}")

        # Extract headings
        headings = container.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        add_debug_log(
            f"Found {len(headings)} headings in container {container_idx+1}")

        for heading_idx, heading in enumerate(headings):
            if heading.get_text(strip=True):
                key = f"heading_{heading.name}_{container_idx}_{heading_idx}"
                results_dict[key] = heading.get_text(strip=True)
                total_headings += 1

        # Extract paragraphs
        paragraphs = container.find_all('p')
        add_debug_log(
            f"Found {len(paragraphs)} paragraphs in container {container_idx+1}")

        for p_idx, paragraph in enumerate(paragraphs):
            if paragraph.get_text(strip=True):
                key = f"paragraph_{container_idx}_{p_idx}"
                results_dict[key] = paragraph.get_text(strip=True)
                total_paragraphs += 1

        # Extract lists
        list_elements = container.find_all(['ul', 'ol'])
        add_debug_log(
            f"Found {len(list_elements)} list elements in container {container_idx+1}")

        for list_idx, list_elem in enumerate(list_elements):
            list_items = list_elem.find_all('li')
            add_debug_log(
                f"Found {len(list_items)} list items in list {list_idx+1}")

            for item_idx, item in enumerate(list_items):
                if item.get_text(strip=True):
                    key = f"list_{list_elem.name}_{container_idx}_{list_idx}_{item_idx}"
                    results_dict[key] = item.get_text(strip=True)
                    total_list_items += 1

    add_debug_log(
        f"Extracted content summary: {total_headings} headings, {total_paragraphs} paragraphs, {total_list_items} list items")

    # If no structured content was found, fall back to the original method
    if not results_dict:
        add_debug_log(
            "No structured content found, falling back to extracting text from all elements")
        fallback_count = 0

        for top_level_child in soup.find_all(recursive=True):
            for index, child in enumerate(top_level_child.descendants):
                if isinstance(child, NavigableString) and child.strip():
                    results_dict[f"{top_level_child.name}_{index}"] = child.strip()
                    fallback_count += 1

                    # Only log the first few items to avoid excessive logging
                    if fallback_count <= 5:
                        add_debug_log(
                            f"Extracted text from {top_level_child.name}: {child.strip()[:50]}...")

        add_debug_log(
            f"Fallback method extracted {fallback_count} text elements")

    add_debug_log(f"Final result contains {len(results_dict)} elements")

    return results_dict


class DefaultParser:
    """Default text extractor"""

    def __init__(self) -> None:
        pass

    def parse_article(self, url: str) -> dict:
        add_debug_log(f"DefaultParser: Starting to parse URL: {url}")

        try:
            add_debug_log("DefaultParser: Sending HTTP request")
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            add_debug_log(
                f"DefaultParser: Received response with status code: {response.status_code}")

            if response.status_code != 200:
                add_debug_log(
                    f"DefaultParser: Error - HTTP status code {response.status_code}")
                return {}

            content_type = response.headers.get('Content-Type', '')
            add_debug_log(f"DefaultParser: Content-Type: {content_type}")

            # Debug response content preview
            content_preview = response.text[:500] + \
                "..." if len(response.text) > 500 else response.text
            add_debug_log(
                f"DefaultParser: Response content preview: {content_preview}")

        except Exception as e:
            add_debug_log(
                f"DefaultParser: Error making HTTP request: {str(e)}")
            return {}

        try:
            add_debug_log("DefaultParser: Creating BeautifulSoup object")
            soup = BeautifulSoup(response.content, 'html.parser')
            add_debug_log(
                f"DefaultParser: BeautifulSoup object created successfully")
        except Exception as e:
            add_debug_log(
                f"DefaultParser: Error creating BeautifulSoup object: {str(e)}")
            return {}

        add_debug_log(
            "DefaultParser: Calling getSoupResults to extract content")
        results = getSoupResults(soup)
        add_debug_log(
            f"DefaultParser: Extraction complete, found {len(results)} elements")

        return results


class SeleniumParser:
    """Extract text using Selenium"""

    def __init__(self) -> None:
        pass

    def parse_article(self, url: str) -> dict:
        add_debug_log(f"SeleniumParser: Starting to parse URL: {url}")

        try:
            add_debug_log("SeleniumParser: Initializing Chrome WebDriver")
            driver = webdriver.Chrome()
            add_debug_log(
                f"SeleniumParser: WebDriver initialized successfully")

            add_debug_log(f"SeleniumParser: Navigating to URL: {url}")
            driver.get(url)
            add_debug_log("SeleniumParser: Page loaded successfully")

            # Extract data from the rendered page
            add_debug_log("SeleniumParser: Getting page source")
            page_source = driver.page_source
            add_debug_log(
                f"SeleniumParser: Page source retrieved, length: {len(page_source)} characters")

            # Close the WebDriver
            add_debug_log("SeleniumParser: Closing WebDriver")
            driver.quit()
            add_debug_log("SeleniumParser: WebDriver closed successfully")

        except Exception as e:
            add_debug_log(f"SeleniumParser: Error with Selenium: {str(e)}")
            return {}

        try:
            add_debug_log("SeleniumParser: Creating BeautifulSoup object")
            soup = BeautifulSoup(page_source, 'html.parser')
            add_debug_log(
                "SeleniumParser: BeautifulSoup object created successfully")
        except Exception as e:
            add_debug_log(
                f"SeleniumParser: Error creating BeautifulSoup object: {str(e)}")
            return {}

        add_debug_log(
            "SeleniumParser: Calling getSoupResults to extract content")
        results = getSoupResults(soup)
        add_debug_log(
            f"SeleniumParser: Extraction complete, found {len(results)} elements")

        return results
