from . import helpers
from . import tasks
from . import constants
from fuzzywuzzy import process


def process_request(text, session_id):
    scholarships_list = []
    speech = "server error"
    dashboard_link = ""
    options_list = []
    check_box = False
    try:
        api_ai_response = tasks.call_third_party_api(post_data=
                                                     {"query": text,
                                                      "sessionId": session_id,
                                                      "lang": "en"})
        result = api_ai_response.get('result')
    except Exception:
        speech = "Could not connect to text processor."
    if result:
        fulfillment = result.get('fulfillment')
        if fulfillment:
            speech = fulfillment.get('speech')
        action = result.get('action')
        action_complete = not (result.get('actionIncomplete'))
        contexts = result.get('contexts')
        contexts_name_list = [context['name'] for context in contexts]
        options_list, check_box = get_options(contexts_name_list, action)
        if action_complete and action == "find-scholarship":
            try:
                search_result = tasks.search_scholarships(result['parameters'])
                scholarships_list = search_result['data']['matchingScholarships']
                if len(scholarships_list) == 0:
                    speech = "I could not find any scholarships for this search criteria"
                else:
                    dashboard_link = search_result['data']['dashboardLink']
            except Exception:
                speech = search_result.get("error").get("errorMessage")
        elif action_complete and action == "check-eligibility":
            scholarship = result['parameters']['scholarship']
            religion = result['parameters']['religion']
            scholarship_class = result['parameters']['class']
            gender = result['parameters']['gender']
            params = [religion, gender, scholarship_class]
            schol_id = helpers.get_matching_schol(scholarship)
            actual_scholarship = tasks.get_schol_info(scholarship).get("Title")
            result = check_eligibility(schol_id, params)
            if result:
                speech = "You are Eligible for {scholarship_title}".format(scholarship_title=actual_scholarship)
            else:
                speech = "You are Not Eligible for {scholarship_title}".format(scholarship_title=actual_scholarship)
        elif action_complete and action == "scholarship-info":
            scholarship = result['parameters']['scholarship']
            schol_info = tasks.get_schol_info(scholarship)

            if schol_info.get("Title") is None:
                speech = "Can't find scholarship " + scholarship
            else:
                speech = schol_info.get("Title") + \
                         "\nDead Line: " + schol_info.get("Deadline") + \
                         "\nAward Money: " + schol_info.get("Award") + \
                         "\nEligibility: " + schol_info.get("Eligibility") + \
                         "\nApply at: " + schol_info.get("URL")
        elif action_complete and action == "report-problem":
            params = {"contactNumber": result['parameters']['phone'],
                      "emailAddress": result['parameters']['email'],
                      "message": result['parameters']['problem'],
                      "name": result['parameters']['name']}
            tasks.submit_query(params)
        elif action_complete and action == "request-call":
            params = {"contactNumber": result['parameters']['phone'],
                      "emailAddress": result['parameters']['email'],
                      "message": "Call request",
                      "name": result['parameters']['name']}
            tasks.submit_query(params)
        if action_complete and not action == "input.unknown":
            options_list, check_box = get_options([], "startup")
    return {
        "scholarships": scholarships_list,
        "options": options_list,
        "text": speech,
        "dashboard_link": dashboard_link,
        "checkBox": check_box
    }


def get_options(contexts_name_list, action):
    all_options = []
    flag = False
    if action == "input.unknown":
        all_options = constants.OPTIONS.get("fallback")
    elif action == "find-scholarship":
        if constants.CONTEXTS_NAME_LIST["context_class"] in contexts_name_list:
            all_options = helpers.get_options("class")
        if constants.CONTEXTS_NAME_LIST["context_gender"] in contexts_name_list:
            all_options = helpers.get_options("gender")
        if constants.CONTEXTS_NAME_LIST["context_religion"] in contexts_name_list:
            all_options = helpers.get_options("religion")
        if constants.CONTEXTS_NAME_LIST["context_interest_area"] in contexts_name_list:
            all_options = helpers.get_options("special")
            flag = True
    elif action == "startup":
        all_options = constants.OPTIONS.get("start_up")

    return list(all_options), flag


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


def get_schol_rules(schol_id):
    rules = []
    rule_list = []
    schol_list = helpers.get_schol_list()
    for schol in schol_list:
        schol_nid = schol.get("NID")
        if schol_nid == schol_id:
            rules = schol.get("SCHOLARSHIP_RULES")
        rule_list = []
        for rule in rules:
            rule_list.append(str(rule['rule']))
    return rule_list


def check_eligibility(schol_id, param):
    schol_rules = get_schol_rules(schol_id)
    print(schol_rules)
    param_rules = helpers.convert_to_rules(param)
    print(param_rules)
    count = 0
    for param_rule in param_rules:
        if param_rule in schol_rules:
            count += 1
    if count >= len(param_rules):
        return True
    else:
        return False
