from flask import Flask, render_template, request
from parsers import DefaultParser
from parsers import SeleniumParser
from parsers import get_debug_logs
from urllib.parse import urlparse
import json
from repo import insert


def get_domain_name(url: str) -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.split('.')
    domain_name = domain[0] if domain[0] != 'www' else domain[1]
    return domain_name


def scrape_webpage(url: str) -> dict:
    urlDomain = get_domain_name(url)

    return {
        'nytimes': SeleniumParser(),
    }.get(urlDomain, DefaultParser()).parse_article(url)

# Rest of your code


# Flask web application
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form['url']
        print("Got URL: ")
        print(url)

        parsed_elements = scrape_webpage(url)

        # Convert the results_dict to a JSON string
        json_result = json.dumps(parsed_elements, indent=4)

        for key in parsed_elements:
            insert(key=key, val=parsed_elements[key])

        # Specify the file path where you want to save the JSON data
        file_path = "testdata/output.json"
        # Save the JSON data to a file
        with open(file_path, "w") as json_file:
            json_file.write(json_result)

        # Get debug logs
        debug_log_html = get_debug_logs()

        # Create a summary that includes both the result count and debug logs
        summary_html = f"""
        <div class="results-summary">
            <p>Number of elements extracted: {len(parsed_elements)}</p>
        </div>
        <div class="debug-logs">
            {debug_log_html}
        </div>
        """

        return render_template('result.html',
                               summary=summary_html,
                               title='URL Parsing Results',
                               abstract=f"Parsed {url}" if len(parsed_elements) > 0 else f"No results found for {url}")
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
