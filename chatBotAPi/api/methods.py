from . import tasks
from . import constants
from fuzzywuzzy import process


def process_request(text, session_id):
    api_ai_response = tasks.call_third_party_api(post_data=
                                                 {"query": text,
                                                  "sessionId": session_id,
                                                  "lang": "en"})
    result = api_ai_response.get('result')
    scholarships_list = []
    speech = "server error"
    if result:
        fulfillment = result.get('fulfillment')
        if fulfillment:
            speech = fulfillment.get('speech')
        action = result.get('action')
        action_complete = not (result.get('actionIncomplete'))
        contexts = result.get('contexts')
        contexts_name_list = [context['name'] for context in contexts]
        options_list = get_options(contexts_name_list, action)
        if action_complete and action == "find-scholarship":
            search_result = tasks.call_search_api(api_ai_response)
            scholarships_list = search_result['response']['scholarships']
        elif action_complete and action == "check-eligibility":
            count = 0
            scholarship = result['parameters']['scholarship']
            religion = result['parameters']['religion']
            scholarship_class = result['parameters']['class']
            gender = result['parameters']['gender']
            actual_scholarship, actual_scholarship_rules = get_scholarship_info(scholarship)
            for rules in actual_scholarship_rules:
                if religion or "For All" in rules['rulename']:
                    count += 1
                if scholarship_class in rules['rulename']:
                    count += 1
                if gender in rules['rulename']:
                    count += 1
            if count == 3:
                speech = "You are Eligible for {scholarship_title}".format(scholarship_title=actual_scholarship)
            else:
                speech = "You are Not Eligible for {scholarship_title}".format(scholarship_title=actual_scholarship)
        elif action_complete and action == "scholarship-info":
            scholarship = result['parameters']['scholarship']
            scholarship_auth_token = tasks.call_auth_api()
            data_list = tasks.call_scholarships_api(scholarship_auth_token)
            scholarship_dict = create_scholarship_dict(data_list)
            actual_scholarship = (process.extractOne(scholarship, scholarship_dict.keys()))[0]
            print(actual_scholarship)
            if actual_scholarship in scholarship_dict:
                scholarship_nid = scholarship_dict[actual_scholarship]
                scholarship_detail = tasks.call_scholarship_detail_api(scholarship_nid, scholarship_auth_token)
                speech = scholarship_detail
        elif action_complete and action == "report-problem":
            pass
        elif action_complete and action == "request-call":
            pass
        if action_complete:
            options_list = get_options([], "startup")
        return {
            "scholarships": scholarships_list,
            "options": options_list,
            "text": speech
        }


def get_options(contexts_name_list, action):
    all_options = []
    if action == "input.unknown":
        all_options = constants.OPTIONS.get("fallback")
    elif action == "find-scholarship":
        if constants.CONTEXTS_NAME_LIST["context_class"] in contexts_name_list:
            all_options = (constants.OPTIONS.get("search_scholarship")).get("class")
        if constants.CONTEXTS_NAME_LIST["context_gender"] in contexts_name_list:
            all_options = (constants.OPTIONS.get("search_scholarship")).get("gender")
        if constants.CONTEXTS_NAME_LIST["context_religion"] in contexts_name_list:
            all_options = (constants.OPTIONS.get("search_scholarship")).get("religion")
        if constants.CONTEXTS_NAME_LIST["context_interest_area"] in contexts_name_list:
            all_options = (constants.OPTIONS.get("search_scholarship")).get("interest_area")
    elif action == "startup":
        all_options = constants.OPTIONS.get("start_up")

    return list(all_options)


def get_scholarship_info(scholarship):
    scholarship_auth_token = tasks.call_auth_api()
    data_list = tasks.call_scholarships_api(scholarship_auth_token)
    scholarship_dict = create_scholarship_dict(data_list)
    actual_scholarship = (process.extractOne(scholarship, scholarship_dict.keys()))[0]
    actual_scholarship_rules = create_scholarship_rules(actual_scholarship, data_list)
    return actual_scholarship, actual_scholarship_rules


def create_scholarship_dict(data_list):
    scholarship_dict = dict()
    for scholarship in data_list:
        scholarship_dict[scholarship['TITLE']] = scholarship['NID']
    return scholarship_dict


def create_scholarship_rules(actual_scholarship, data_list):
    scholarship_rules = []
    if actual_scholarship in data_list:
        scholarship_rules = data_list['SCHOLARSHIP_RULES']
    return scholarship_rules
