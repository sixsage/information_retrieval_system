import requests
import openai
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os

# response = requests.get('https://www.informatics.uci.edu/explore/faculty-profiles/cristina-lopes/')
# soup = BeautifulSoup(response.text, 'lxml')

# content = soup.get_text()
# # print(content)
# # print(len(content))
# lines = [line.strip() for line in content.splitlines()]
# phrases = [phrase.strip() for phrase in lines]
# result = '\n'.join(phrase for phrase in phrases if phrase)
# print(result[:4000])
# print(len(result))

load_dotenv()
openai.api_key = os.environ.get('openai-token')

def generate_summary(url):
    '''
    Given a url, get the content of the url's webpage.
    If there is a valid response, return the summary.
    If there were no valid response, return error message.
    '''

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')

        content = soup.get_text()
        lines = [line.strip() for line in content.splitlines()]
        phrases = [phrase.strip() for phrase in lines]
        result = '\n'.join(phrase for phrase in phrases if phrase)
        result = result[:4000]
        result += '\nPlease summarize the above webpage content in less than 60 words'
        # pass in result to openai
        gpt_response = openai.Completion.create(
            model="gpt-3.5-turbo-0613",
            message = [{'role': 'user', 'content': result}]
        )
        return gpt_response['choices'][0]['message']['content'].strip()
    else:
        return 'Summary unavailable'