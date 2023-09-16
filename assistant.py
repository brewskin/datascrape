from flask import Flask, render_template, request
from parsers import DefaultParser
from parsers import SeleniumParser
import openai
from urllib.parse import urlparse
import json

# OpenAI API configuration
openai.api_key = 'YOUR_OPENAI_API_KEY'


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


# Summarization function using ChatGPT
def generate_summary(text):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=text,
        max_tokens=100,
        temperature=0.7
    )
    # Extract and return the generated summary from the response
    return response.choices[0].text.strip()


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

        # Specify the file path where you want to save the JSON data
        file_path = "output.json"

        # Save the JSON data to a file
        with open(file_path, "w") as json_file:
            json_file.write(json_result)

        print(f"JSON data saved to {file_path}")

        return render_template('result.html', summary='Read File', title=parsed_elements['title'], abstract=parsed_elements['html'])
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
