from flask import Flask, render_template, request
from parsers import DefaultParser
from parsers import SeleniumParser
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

        return render_template('result.html', summary='Read File', title='The Process is Complete', abstract=len(parsed_elements))
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
