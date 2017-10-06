OPTIONS = {
    "start_up": [{"name": "Find Scholarships"}, {"name": "Check Eligibility"}, {"name": "Report Problem"},
                 {"name": "Scholarship Information"}],
    "search_scholarship": {
        "class": [{"name": "10th"}, {"name": "12th"}, {"name": "Graduate"}, {"name": "Post Graduate"},
                  {"name": "Skip"}],
        "religion": [{"name": "Hindu"}, {"name": "Muslim"}, {"name": "Sikh"}, {"name": "Christian"},
                     {"name": "Buddhism"}, {"name": "Skip"}],
        "gender": [{"name": "Male"}, {"name": "Female"}, {"name": "Skip"}],
        "interest_area": [{"name": "Merit"}, {"name": "Low Income"}, {"name": "Sports"}, {"name": "Science"},
                          {"name": "Maths"}, {"name": "Literary Art"}, {"name": "Skip"}],
    },
    "fallback": [{"name": "Report Problem"}, {"name": "Request a Call"}]

}

CONTEXTS_NAME_LIST = {
    "context_class": "search_scholarship_dialog_params_class",
    "context_gender": "search_scholarship_dialog_params_gender",
    "context_religion": "search_scholarship_dialog_params_religion",
    "context_interest_area": "search_scholarship_dialog_params_interest-area",
}
