from . import helpers
from . import tasks
from . import constants

from datetime import date


def process_request(text, session_id, user_id):
    scholarships_list = []
    speech = "server error"
    dashboard_link = ""
    options_list = []
    check_box = False
    is_missing = False
    missing_fields = []
    api_ai_response = ""
    schol_info_result = {}
    result = {}
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
        print(action)
        action_complete = not (result.get('actionIncomplete'))
        contexts = result.get('contexts')
        contexts_name_list = [context['name'] for context in contexts]
        options_list, check_box = get_options(contexts_name_list, action)

        if action_complete and action != "confirm-signup" and action != "ask-missing-field":
            options_list, check_box = get_options([], "startup")

        if action_complete and action == "sign-up":
            speech = "<a href='http://www.learningwithvodafone.in'>Click here to sign up.</a>"

        if action_complete and action == "find-scholarship":
            try:
                search_result = tasks.search_scholarships(result['parameters'])
                scholarships_list = search_result['data']['matchingScholarships']
                print(scholarships_list)
                scholarships_list = remove_invalid_scholarships(scholarships_list)
                print(scholarships_list)
                dashboard_link = search_result['data']['dashboardLink']
                user_id = search_result['data']['userId']
                tasks.call_third_party_api(post_data=
                                           {"query": "user-signed-in",
                                            "sessionId": session_id,
                                            "lang": "en"})
                if len(scholarships_list) == 0:
                    speech = "I could not find any matching scholarships for you."
                else:
                    if len(scholarships_list) >= 4:
                        speech = "Based on your profile here are your 4 out of {schol_num} matched scholarships".format(
                            schol_num=len(scholarships_list))
                    elif len(scholarships_list) == 1:
                        speech = "Based on your profile here is your matched scholarship"
                    else:
                        speech = "Based on your profile here are your {schol_num} matched scholarships".format(
                            schol_num=len(scholarships_list))
            except Exception:
                speech = search_result.get("error").get("errorMessage")
                if speech.find("Mobile") != -1:
                    temp_response = tasks.call_third_party_api(post_data=
                                                               {"query": "ask-mobile-number",
                                                                "sessionId": session_id,
                                                                "lang": "en"})
                    options_list, check_box = get_options(contexts_name_list, temp_response.get("result").get("action"))
                    speech = temp_response.get("result").get("fulfillment").get("speech")
                elif speech.find("Email") != -1:
                    temp_response = tasks.call_third_party_api(post_data=
                                                               {"query": "ask-email",
                                                                "sessionId": session_id,
                                                                "lang": "en"})
                    options_list, check_box = get_options(contexts_name_list, temp_response.get("result").get("action"))
                    speech = temp_response.get("result").get("fulfillment").get("speech")
                else:
                    tasks.call_third_party_api(post_data=
                                               {"query": "clear-saved-param",
                                                "sessionId": session_id,
                                                "lang": "en"})

        elif action_complete and action == "check-eligibility":
            scholarship = result['parameters']['scholarship']
            religion = result['parameters']['religion']
            scholarship_class = result['parameters']['class']
            gender = result['parameters']['gender']
            params = [religion, gender, scholarship_class]
            schol_id, score = helpers.get_matching_schol(scholarship)
            if (score > 70):
                schol_info = tasks.get_schol_info(scholarship)
                schol_url = schol_info.get("URL")
                actual_scholarship = schol_info.get("Title")
                eligibility_result = check_eligibility(schol_id, params)
                if eligibility_result:
                    speech = "You are Eligible for {scholarship_title}. \
                    <a href='{scholarship_url}'>Click here for more info.</a>".format(
                        scholarship_title=actual_scholarship, scholarship_url=schol_url)
                else:
                    speech = "You are Not Eligible for {scholarship_title}. \
                    <a href='{scholarship_url}'>Click here for more info.</a>".format(
                        scholarship_title=actual_scholarship, scholarship_url=schol_url)
            else:
                speech = "Scholarship not found."
        elif action_complete and action == "scholarship-info":
            scholarship = result['parameters']['scholarship']
            schol_info = tasks.get_schol_info(scholarship)
            schol_info_result = {}

            if schol_info.get("Title") is None:
                speech = "Can't find scholarship " + scholarship
            else:
                speech = "<a href= '" + schol_info.get("URL") + "'>" + schol_info.get("Title") + "</a>" + \
                         "<br> Dead Line: " + str(schol_info.get("Deadline")) + \
                         "<br> Award Money: " + schol_info.get("Award") + \
                         "<br> Eligibility: " + schol_info.get("Eligibility") + \
                         "<br> <a href= '" + schol_info.get("URL") + "'>Apply here </a>"
                schol_info_result = {
                    "nid": schol_info.get("Nid"),
                    "detailsUrl": schol_info.get("URL"),
                    "scholarshipTitle": schol_info.get("Title"),
                    "awardMoney": schol_info.get("Award"),
                    "eligibility": schol_info.get("Eligibility"),
                    "deadline": schol_info.get("Deadline")
                }

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
            print(tasks.find_schol_userid(user_id))
            scholarships_list = remove_invalid_scholarships(tasks.find_schol_userid(user_id))
            print(scholarships_list)
            if len(scholarships_list) == 0:
                speech = "I could not find any matching scholarships for you."
            else:
                if len(scholarships_list) >= 4:
                    speech = "Based on your profile here are your 4 out of {schol_num} matched scholarships".format(
                        schol_num=len(scholarships_list))
                elif len(scholarships_list) == 1:
                    speech = "Based on your profile here is your matched scholarship"
                else:
                    speech = "Based on your profile here are your {schol_num} matched scholarships".format(
                        schol_num=len(scholarships_list))

        elif action_complete and action == "update-missing-field":
            missing_field = result['parameters']['field']
            value = result['parameters']['value']
            if missing_field == "Class" or missing_field == "Gender":
                contexts_name_list.append(missing_field)
                value = helpers.convert_to_rules([value])[0]
                tasks.update_user_rule(user_id, value)
            else:
                tasks.update_user(user_id, missing_field, value)

        elif action_complete and action == "get-missing-fields":
            if user_id:
                missing_fields = tasks.get_missing_fields(user_id)
                if len(missing_fields) > 0:
                    is_missing = True

        elif action_complete and action == "check-eligibility-userid":
            scholarship = result['parameters']['scholarship']
            schol_info = tasks.get_schol_info(scholarship)
            actual_scholarship = schol_info.get("Title")
            schol_url = schol_info.get("URL")
            nid, score = helpers.get_matching_schol(scholarship)
            if score > 70:
                if user_id:
                    schol_list = tasks.find_schol_userid(user_id)
                    found = False
                    for schol in schol_list:
                        if schol.get("nid") == nid:
                            found = True
                    if found:
                        speech = "You are Eligible for {scholarship_title}. \
                        <a href='{scholarship_url}'>Click here for more info.</a>".format(
                            scholarship_title=actual_scholarship, scholarship_url=schol_url)
                    else:
                        speech = "You are Not Eligible for {scholarship_title}. \
                        <a href='{scholarship_url}'>Click here for more info.</a>".format(
                            scholarship_title=actual_scholarship, scholarship_url=schol_url)
            else:
                speech = "Scholarship " + scholarship + " not found."

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

        if action == "startup" or action == "input.unknown" and action_complete:
            if user_id:
                try:
                    tasks.call_third_party_api(post_data=
                                               {"query": "user-signed-in",
                                                "sessionId": session_id,
                                                "lang": "en"})
                except Exception:
                    speech = "Could not connect to text processor."
    if user_id:
        if "Sign Up" in options_list:
            options_list = options_list.copy()
            options_list.remove("Sign Up")
    output = {
        "scholarships": scholarships_list,
        "options": options_list,
        "text": speech,
        "dashboard_link": dashboard_link,
        "checkBox": check_box,
        "missingFields": missing_fields,
        "isMissing": is_missing,
        "api_ai_response": api_ai_response,
        "userId": user_id
    }
    if schol_info_result:
        output["scholInfo"] = schol_info_result
    return output


def get_options(contexts_name_list, action):
    all_options = []
    flag = False
    if action == "input.unknown":
        all_options = constants.OPTIONS.get("fallback")
    elif action == "find-scholarship" or action == "check-eligibility" or action == "update-missing-field":
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
    elif action == "ask-missing-field" or action == "confirm-signup":
        all_options = constants.OPTIONS.get("ask_missing_field")
    print(all_options)
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


def remove_invalid_scholarships(scholarship_list):
    out_list = []
    for schol in scholarship_list:
        scholarship = tasks.get_schol_info_nid(schol.get("nid"))
        deadline = scholarship.get("Deadline")
        if deadline > str(date.today()):
            out_list.append(schol)
    return out_list
