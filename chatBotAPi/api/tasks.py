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


def call_auth_api():
    try:
        url = "{auth_api}".format(auth_api=get_secret("AUTH_API"))
        response = requests.post(url)
        return response.json()['BODY']['DATA']['TOKEN']
    except Exception:
        return None


def call_scholarships_api(scholarship_auth_token):
    try:
        url = "{scholarship_api_url}".format(scholarship_api_url=get_secret("SCHOLARSHIP_API_URL"))
        headers = {'B4SAUTH': scholarship_auth_token}
        response = requests.post(url, headers=headers)
        return response.json()['BODY']['DATA']
    except Exception:
        return None


def call_scholarship_detail_api(scholarship_nid, scholarship_auth_token):
    try:
        url = "{scholarship_detail_api_url}/{nid}".format(
            scholarship_detail_api_url=get_secret("SCHOLARSHIP_DETAIL_API_URL"), nid=scholarship_nid)
        headers = {'B4SAUTH': scholarship_auth_token}
        response = requests.get(url, headers=headers)
        return response.json()['BODY']['RECOMENDED'][0]
    except Exception:
        return None
