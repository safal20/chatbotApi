from api import tasks
from api import constants


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
        search_result = tasks.call_search_api(api_ai_response)
        if action_complete:
            scholarships_list = search_result['response']['scholarships']
        return {
            "scholarships": scholarships_list,
            "options": options_list,
            "text": speech
        }


def get_options(contexts_name_list, action):
    all_options = []
    if action == "action.unknown":
        all_options = constants.OPTIONS['fallback']
    elif action == "find-scholarship":
        if constants.CONTEXTS_NAME_LIST["context_class"] in contexts_name_list:
            all_options = (constants.OPTIONS.get("search_scholarship")).get("class")
        if constants.CONTEXTS_NAME_LIST["context_gender"] in contexts_name_list:
            all_options = (constants.OPTIONS.get("search_scholarship")).get("gender")
        if constants.CONTEXTS_NAME_LIST["context_religion"] in contexts_name_list:
            all_options = (constants.OPTIONS.get("search_scholarship")).get("religion")
        if constants.CONTEXTS_NAME_LIST["context_interest_area"] in contexts_name_list:
            all_options = (constants.OPTIONS.get("search_scholarship")).get("interest_area")

    return list(all_options)
