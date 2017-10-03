import json

import requests

from config.settings.base import get_secret

api_ai = get_secret("API_AI")


def call_third_party_api(post_data):
    try:
        api_key = "Bearer {api_ai_key}".format(api_ai_key=get_secret("API_AI_KEY"))
        url = "{api_path}".format(api_path=api_ai)
        headers = {'Content-Type': 'application/json', 'Authorization': api_key}
        response = requests.post(url, data=json.dumps(post_data),
                                 headers=headers)
        return response.json()
    except Exception:
        return None


def call_search_api(data):
    try:
        url = "{search_api_path}".format(search_api_path=get_secret("SEARCH_API_PATH"))
        response = requests.post(url, data=json.dumps(data))
        return response.json()
    except Exception:
        return None