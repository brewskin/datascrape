import os
import openai

# OpenAI API configuration
openai.api_key = os.environ['OPENAI_KEY']

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
