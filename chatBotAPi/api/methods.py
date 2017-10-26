from . import helpers
from . import tasks
from . import constants


def process_request(text, session_id, user_id):
    scholarships_list = []
    speech = "server error"
    dashboard_link = ""
    options_list = []
    check_box = False
    is_missing = False
    missing_fields = []
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
                         "\nDead Line: " + str(schol_info.get("Deadline")) + \
                         "\nAward Money: " + schol_info.get("Award") + \
                         "\nEligibility: " + schol_info.get("Eligibility") + \
                         "\nApply at: " + schol_info.get("URL")

        elif action_complete and action == "report-problem":
            params = {"contactNumber": result['parameters']['phone'],
                      "emailAddress": result['parameters']['email'],
                      "message": result['parameters']['problem'],
                      "name": result['parameters']['first_name'] + " " + result['parameters']['last_name']}
            tasks.submit_query(params)

        elif action_complete and action == "request-call":
            params = {"contactNumber": result['parameters']['phone'],
                      "emailAddress": result['parameters']['email'],
                      "message": "Call request",
                      "name": result['parameters']['first_name'] + " " + result['parameters']['last_name']}
            tasks.submit_query(params)

        elif action_complete and action == "find-scholarship-userid":
            scholarships_list = tasks.find_schol_userid(user_id)

        elif action_complete and action == "update-missing-field":
            missing_field = result['parameters']['field']
            value = result['parameters']['value']
            print(missing_field, value)

            tasks.update_user(user_id, missing_field, value)

        elif action_complete and action == "get-missing-fields":
            if user_id:
                missing_fields = tasks.get_missing_fields(user_id)
                if len(missing_fields) > 0:
                    is_missing = True

        elif action_complete and action == "check-eligibility-userid":
            scholarship = result['parameters']['scholarship']
            actual_scholarship = tasks.get_schol_info(scholarship).get("Title")
            nid = helpers.get_matching_schol(scholarship)
            if user_id:
                schol_list = tasks.find_schol_userid(user_id)
                found = False
                for schol in schol_list:
                    if schol.get("nid") == nid:
                        found = True
                if found:
                    speech = "You are eligible for " + actual_scholarship
                else:
                    speech = "You are not eligible for " + actual_scholarship

        elif action_complete and action == "report-problem-userid":
            if user_id:
                details = tasks.get_user_details(user_id)
                params = {"contactNumber": details.get("phone"),
                          "emailAddress": details.get("email"),
                          "message": result['parameters']['problem'],
                          "name": details.get("name")}
                tasks.submit_query(params)

        elif action_complete and action == "request-call-userid":
            if user_id:
                details = tasks.get_user_details(user_id)
                params = {"contactNumber": details.get("phone"),
                          "emailAddress": details.get("email"),
                          "message": "Call request",
                          "name": details.get("name")}
                tasks.submit_query(params)

        if action_complete:
            options_list, check_box = get_options([], "startup")
        if action == "startup" or action == "input.unknown" and action_complete:
            if user_id:
                try:
                    tasks.call_third_party_api(post_data=
                                               {"query": "user-signed-in",
                                                "sessionId": session_id,
                                                "lang": "en"})
                except Exception:
                    speech = "Could not connect to text processor."
    return {
        "scholarships": scholarships_list,
        "options": options_list,
        "text": speech,
        "dashboard_link": dashboard_link,
        "checkBox": check_box,
        "missingFields": missing_fields,
        "isMissing": is_missing
    }


def get_options(contexts_name_list, action):
    all_options = []
    flag = False
    if action == "input.unknown":
        all_options = constants.OPTIONS.get("fallback")
    elif action == "find-scholarship" or action == "check-eligibility":
        for context in contexts_name_list:
            if "class" in context:
                all_options = helpers.get_options("class")
        for context in contexts_name_list:
            if "gender" in context:
                all_options = helpers.get_options("gender")
        for context in contexts_name_list:
            if "religion" in context:
                all_options = helpers.get_options("religion")
        for context in contexts_name_list:
            if "interest" in context:
                all_options = helpers.get_options("special")
                flag = True
    elif action == "startup":
        all_options = constants.OPTIONS.get("start_up")

    return list(all_options), flag


def check_eligibility(schol_id, param):
    schol_rules = helpers.transform_rules(helpers.get_schol_rules(schol_id))
    param_rules = helpers.convert_to_rules(param)
    count = 0
    for param_rule in param_rules:
        if param_rule in schol_rules:
            count += 1
    if count == len(param_rules):
        return True
    else:
        return False
