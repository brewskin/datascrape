from bs4 import BeautifulSoup
from bs4 import Tag
from bs4 import NavigableString
import requests
from selenium import webdriver

# Global debug log list to store debug information
debug_logs = []


def add_debug_log(message, level="INFO"):
    """
    Add a debug message to the global debug logs

    Args:
        message: The message to log
        level: Log level (INFO, WARNING, ERROR, SUCCESS)
    """
    log_entry = {
        "message": message,
        "level": level
    }
    debug_logs.append(log_entry)
    print(f"DEBUG [{level}]: {message}")


def get_debug_logs():
    """Get all debug logs as HTML formatted string with improved styling"""
    if not debug_logs:
        return "<p>No debug logs recorded</p>"

    log_html = """
    <h3>Debug Logs:</h3>
    <div class="log-controls">
        <button onclick="toggleAllLogs()">Toggle All Logs</button>
        <button onclick="expandAllLogs()">Expand All</button>
        <button onclick="collapseAllLogs()">Collapse All</button>
    </div>
    <div class="log-container">
    """

    # Group logs by section for better organization
    current_section = "Initialization"
    log_html += f'<div class="log-section"><h4>{current_section}</h4><ul>'

    for i, log in enumerate(debug_logs):
        level = log.get("level", "INFO")
        message = log.get("message", "")

        # Detect section changes based on message content
        if "Starting to parse URL" in message:
            current_section = "URL Parsing"
            log_html += '</ul></div>'
            log_html += f'<div class="log-section"><h4>{current_section}</h4><ul>'
        elif "Creating BeautifulSoup object" in message:
            current_section = "HTML Parsing"
            log_html += '</ul></div>'
            log_html += f'<div class="log-section"><h4>{current_section}</h4><ul>'
        elif "Looking for article containers" in message:
            current_section = "Content Extraction"
            log_html += '</ul></div>'
            log_html += f'<div class="log-section"><h4>{current_section}</h4><ul>'
        elif "Extraction complete" in message:
            current_section = "Results"
            log_html += '</ul></div>'
            log_html += f'<div class="log-section"><h4>{current_section}</h4><ul>'

        # Add CSS class based on log level
        css_class = f"log-{level.lower()}"

        # For long messages, create collapsible content
        if len(message) > 100:
            short_message = message[:100] + "..."
            log_html += f"""
            <li class="{css_class}" id="log-{i}">
                <div class="log-header" onclick="toggleLog({i})">
                    <span class="log-indicator">▶</span> {short_message}
                </div>
                <div class="log-content" style="display:none;">
                    {message}
                </div>
            </li>
            """
        else:
            log_html += f'<li class="{css_class}">{message}</li>'

    log_html += '</ul></div>'

    # Add JavaScript for interactive logs
    log_html += """
    <script>
    function toggleLog(id) {
        const logItem = document.getElementById('log-' + id);
        const content = logItem.querySelector('.log-content');
        const indicator = logItem.querySelector('.log-indicator');
        
        if (content.style.display === 'none') {
            content.style.display = 'block';
            indicator.textContent = '▼';
        } else {
            content.style.display = 'none';
            indicator.textContent = '▶';
        }
    }
    
    function expandAllLogs() {
        document.querySelectorAll('.log-content').forEach(el => {
            el.style.display = 'block';
        });
        document.querySelectorAll('.log-indicator').forEach(el => {
            el.textContent = '▼';
        });
    }
    
    function collapseAllLogs() {
        document.querySelectorAll('.log-content').forEach(el => {
            el.style.display = 'none';
        });
        document.querySelectorAll('.log-indicator').forEach(el => {
            el.textContent = '▶';
        });
    }
    
    function toggleAllLogs() {
        const sections = document.querySelectorAll('.log-section');
        sections.forEach(section => {
            if (section.style.display === 'none') {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });
    }
    </script>
    </div>
    """

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

    add_debug_log(f"Starting HTML parsing with BeautifulSoup", "INFO")

    results_dict = {}
    results_dict["full_text"] = ""  # Initialize the full_text key

    # Try to find the main article content
    article_containers = []

    # Look for common article container elements
    add_debug_log("Looking for article containers...", "INFO")
    for container in ['article', 'main', 'div.article', 'div.content', 'div.post']:
        if '.' in container:
            tag, class_name = container.split('.')
            found = soup.find_all(tag, class_=class_name)
            if len(found) > 0:
                add_debug_log(
                    f"Searching for {tag} with class {class_name}: found {len(found)} elements", "SUCCESS")
            else:
                add_debug_log(
                    f"Searching for {tag} with class {class_name}: found {len(found)} elements", "INFO")
        else:
            found = soup.find_all(container)
            if len(found) > 0:
                add_debug_log(
                    f"Searching for {container} tag: found {len(found)} elements", "SUCCESS")
            else:
                add_debug_log(
                    f"Searching for {container} tag: found {len(found)} elements", "INFO")

        if found:
            article_containers.extend(found)

    if len(article_containers) > 0:
        add_debug_log(
            f"Total article containers found: {len(article_containers)}", "SUCCESS")
    else:
        add_debug_log(
            f"Total article containers found: {len(article_containers)}", "WARNING")

    # If no specific article containers found, use the body
    if not article_containers:
        add_debug_log(
            "No specific article containers found, falling back to body or entire document", "WARNING")
        if soup.body:
            add_debug_log("Using body tag as container", "INFO")
            article_containers = [soup.body]
        else:
            add_debug_log(
                "No body tag found, using entire document", "WARNING")
            article_containers = [soup]

    # Process each potential article container
    total_headings = 0
    total_paragraphs = 0
    total_list_items = 0

    for container_idx, container in enumerate(article_containers):
        add_debug_log(
            f"Processing container {container_idx+1}/{len(article_containers)}", "INFO")

        # Extract headings
        headings = container.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if len(headings) > 0:
            add_debug_log(
                f"Found {len(headings)} headings in container {container_idx+1}", "SUCCESS")
        else:
            add_debug_log(
                f"Found {len(headings)} headings in container {container_idx+1}", "INFO")

        for heading_idx, heading in enumerate(headings):
            if heading.get_text(strip=True):
                heading_text = heading.get_text(strip=True)
                key = f"heading_{heading.name}_{container_idx}_{heading_idx}"
                results_dict[key] = heading_text
                # Append to full_text with appropriate formatting
                results_dict["full_text"] += f"{heading_text}\n\n"
                total_headings += 1

        # Extract paragraphs
        paragraphs = container.find_all('p')
        if len(paragraphs) > 0:
            add_debug_log(
                f"Found {len(paragraphs)} paragraphs in container {container_idx+1}", "SUCCESS")
        else:
            add_debug_log(
                f"Found {len(paragraphs)} paragraphs in container {container_idx+1}", "INFO")

        for p_idx, paragraph in enumerate(paragraphs):
            if paragraph.get_text(strip=True):
                paragraph_text = paragraph.get_text(strip=True)
                key = f"paragraph_{container_idx}_{p_idx}"
                results_dict[key] = paragraph_text
                # Append to full_text
                results_dict["full_text"] += f"{paragraph_text}\n\n"
                total_paragraphs += 1

        # Extract lists
        list_elements = container.find_all(['ul', 'ol'])
        if len(list_elements) > 0:
            add_debug_log(
                f"Found {len(list_elements)} list elements in container {container_idx+1}", "SUCCESS")
        else:
            add_debug_log(
                f"Found {len(list_elements)} list elements in container {container_idx+1}", "INFO")

        for list_idx, list_elem in enumerate(list_elements):
            list_items = list_elem.find_all('li')
            if len(list_items) > 0:
                add_debug_log(
                    f"Found {len(list_items)} list items in list {list_idx+1}", "SUCCESS")
            else:
                add_debug_log(
                    f"Found {len(list_items)} list items in list {list_idx+1}", "INFO")

            for item_idx, item in enumerate(list_items):
                if item.get_text(strip=True):
                    item_text = item.get_text(strip=True)
                    key = f"list_{list_elem.name}_{container_idx}_{list_idx}_{item_idx}"
                    results_dict[key] = item_text
                    # Append to full_text with bullet point
                    results_dict["full_text"] += f"• {item_text}\n"
                    total_list_items += 1

            # Add an extra newline after each list
            if list_items:
                results_dict["full_text"] += "\n"

    if total_headings > 0 or total_paragraphs > 0 or total_list_items > 0:
        add_debug_log(
            f"Extracted content summary: {total_headings} headings, {total_paragraphs} paragraphs, {total_list_items} list items", "SUCCESS")
    else:
        add_debug_log(
            f"Extracted content summary: {total_headings} headings, {total_paragraphs} paragraphs, {total_list_items} list items", "WARNING")

    # If no structured content was found, fall back to the original method
    if not results_dict:
        add_debug_log(
            "No structured content found, falling back to extracting text from all elements", "WARNING")
        fallback_count = 0

        for top_level_child in soup.find_all(recursive=True):
            for index, child in enumerate(top_level_child.descendants):
                if isinstance(child, NavigableString) and child.strip():
                    text = child.strip()
                    results_dict[f"{top_level_child.name}_{index}"] = text
                    # Append to full_text
                    results_dict["full_text"] += f"{text}\n"
                    fallback_count += 1

                    # Only log the first few items to avoid excessive logging
                    if fallback_count <= 5:
                        add_debug_log(
                            f"Extracted text from {top_level_child.name}: {text[:50]}...", "INFO")

        if fallback_count > 0:
            add_debug_log(
                f"Fallback method extracted {fallback_count} text elements", "SUCCESS")
        else:
            add_debug_log(
                f"Fallback method extracted {fallback_count} text elements", "ERROR")

    if len(results_dict) > 0:
        add_debug_log(
            f"Final result contains {len(results_dict)} elements", "SUCCESS")
    else:
        add_debug_log(
            f"Final result contains {len(results_dict)} elements", "ERROR")

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
        add_debug_log(f"SeleniumParser: Starting to parse URL: {url}", "INFO")

        try:
            add_debug_log(
                "SeleniumParser: Initializing Chrome WebDriver", "INFO")
            driver = webdriver.Chrome()
            add_debug_log(
                f"SeleniumParser: WebDriver initialized successfully", "SUCCESS")

            add_debug_log(f"SeleniumParser: Navigating to URL: {url}", "INFO")
            driver.get(url)
            add_debug_log(
                "SeleniumParser: Page loaded successfully", "SUCCESS")

            # Extract data from the rendered page
            add_debug_log("SeleniumParser: Getting page source", "INFO")
            page_source = driver.page_source
            add_debug_log(
                f"SeleniumParser: Page source retrieved, length: {len(page_source)} characters", "SUCCESS")

            # Close the WebDriver
            add_debug_log("SeleniumParser: Closing WebDriver", "INFO")
            driver.quit()
            add_debug_log(
                "SeleniumParser: WebDriver closed successfully", "SUCCESS")

        except Exception as e:
            add_debug_log(
                f"SeleniumParser: Error with Selenium: {str(e)}", "ERROR")
            return {}

        try:
            add_debug_log(
                "SeleniumParser: Creating BeautifulSoup object", "INFO")
            soup = BeautifulSoup(page_source, 'html.parser')
            add_debug_log(
                "SeleniumParser: BeautifulSoup object created successfully", "SUCCESS")
        except Exception as e:
            add_debug_log(
                f"SeleniumParser: Error creating BeautifulSoup object: {str(e)}", "ERROR")
            return {}

        add_debug_log(
            "SeleniumParser: Calling getSoupResults to extract content", "INFO")
        results = getSoupResults(soup)

        if len(results) > 0:
            add_debug_log(
                f"SeleniumParser: Extraction complete, found {len(results)} elements", "SUCCESS")
        else:
            add_debug_log(
                f"SeleniumParser: Extraction complete, found {len(results)} elements", "WARNING")

        return results
