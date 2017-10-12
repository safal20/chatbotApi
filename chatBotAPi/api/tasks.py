import json

import requests
from api import helpers

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


def get_auth_token():
    try:
        url = "{api_path}".format(api_path=get_secret("CHATBOT_AUTH_API"))
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer'}
        post_data = {"username": get_secret("CHATBOT_USER"), "password": get_secret("CHATBOT_PASS")}
        response = requests.post(url, data=json.dumps(post_data),
                                 headers=headers)
        auth_token = response.json().get('access_token')
        return auth_token

    except Exception:
        return None


def submit_query(params):
    url = "{api_path}".format(api_path=get_secret("QUERY_SUBMISSION_API"))
    auth_token = get_auth_token()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    response = requests.post(url, data=json.dumps(params), headers=headers)
    return response.json()


def find_schol_userid(user_id):
    url = "{api_path}".format(api_path=get_secret("SCHOLARSHIPS_USER").format(user_id=user_id))
    auth_token = get_auth_token()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    response = requests.get(url, headers=headers)
    data = response.json().get('data')
    return data


def get_missing_fields(user_id):
    missing_fields = []
    url = "{api_path}".format(api_path=get_secret("MISSING_FIELDS_API").format(user_id=user_id))
    auth_token = get_auth_token()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    response = requests.get(url, headers=headers)
    data = response.json().get('data')
    if data:
        missing_fields = data.get('missingFields')
    return missing_fields


def search_scholarships(params):
    rules_list = list()
    rules_list.append(params['class'])
    rules_list.append(params['gender'])
    rules_list.append(params['religion'])
    rules = rules_list + params['interest-area']
    post_data = {"email": params['email'],
                 "firstName": params['first_name'],
                 "lastName": params['last_name'],
                 "mobileNumber": params['phone'],
                 "rules": helpers.convert_to_rules(rules)}
    url = "{api_path}".format(api_path=get_secret("USER_REGISTER_API"))
    auth_token = get_auth_token()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token}
    response = requests.post(url, data=json.dumps(post_data), headers=headers)
    return response.json()


def get_schol_info(schol_name):
    schol_id = helpers.get_matching_schol(schol_name)
    schol_info = {}
    auth_token = call_auth_api()
    url = "{api_path}/{nid}".format(api_path=get_secret("SCHOLARSHIP_DETAIL_API_URL"), nid=schol_id)
    headers = {'Content-Type': 'application/json', 'B4SAUTH': auth_token}
    response = requests.get(url, headers=headers)
    body = response.json().get("BODY")
    schol_body = body.get("SCHOLARSHIP_BODY")
    data = body.get("DATA")
    schol_info["Title"] = data.get("TITLE")
    schol_info["Deadline"] = data.get("DEADLINE")
    schol_info["URL"] = get_secret("SCHOLARSHIP_PAGE").format(slug=data.get("SLUG"))
    schol_info["Award"] = data.get("PURPOSE_AWARDS")
    schol_info["Eligibility"] = schol_body.get("ELIGIBILITY")
    return schol_info


def get_scholarships_file():
    auth_token = call_auth_api()
    url = "{api_path}".format(api_path=get_secret("SCHOLARSHIP_API_URL"))
    headers = {'Content-Type': 'application/json', 'B4SAUTH': auth_token}
    response = requests.post(url, headers=headers)
    data = response.json()
    with open(get_secret("SCHOLARSHIPS_JSON_FILE"), 'w') as outfile:
        json.dump(data, outfile)
