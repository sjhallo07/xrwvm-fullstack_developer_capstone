# Uncomment the imports below before you add the function code
import requests
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

backend_url = os.getenv('backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv('sentiment_analyzer_url', default="http://localhost:5050/")


def get_request(endpoint, **kwargs):
    """Perform a GET request to the backend service.

    endpoint: string path starting with '/'
    kwargs: optional query parameters (will be passed as params to requests)
    Returns parsed JSON on success, or None on failure.
    """
    request_url = backend_url + endpoint
    print(f"GET from {request_url} params={kwargs}")
    try:
        response = requests.get(request_url, params=kwargs or None, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Network exception occurred: {err}")
        return None

# def analyze_review_sentiments(text):
# request_url = sentiment_analyzer_url+"analyze/"+text
def analyze_review_sentiments(text):
    # URL-encode the text when embedding it in the path
    quoted = quote_plus(text)
    request_url = f"{sentiment_analyzer_url}analyze/{quoted}"
    try:
        response = requests.get(request_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Sentiment analyzer request failed: {err}")
        return {"sentiment": "neutral"}

def post_review(data_dict):
    request_url = backend_url + "/insert_review"
    try:
        response = requests.post(request_url, json=data_dict, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Failed to post review: {err}")
        return None
# Add code for posting review
