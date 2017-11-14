import csv

import json

from fuzzywuzzy import process
from fuzzywuzzy import fuzz

from config.settings.base import get_secret


# def remove_stopwords(text):
#     stop_words = set(stopwords.words('english'))
#     word_tokens = word_tokenize(text)
#     filtered_sentence = [w for w in word_tokens if not w in stop_words]
#     output_text = " ".join(filtered_sentence)
#     return output_text


def get_rule_list():
    file_obj = open(get_secret("RULE_FILE"))
    reader = csv.reader(file_obj)
    rule_list = []
    for row in reader:
        rule_list.append([row[0], row[2], row[3]])
    return rule_list


def get_rule_dict():
    rule_dict = {}
    rule_list = get_rule_list()
    for rule in rule_list:
        rule_dict[rule[2]] = rule[0]
    return rule_dict


def get_rule_type_dict():
    file_obj = open(get_secret("RULE_TYPE_FILE"))
    reader = csv.reader(file_obj)
    rule_dict = {}
    for row in reader:
        rule_dict[row[1]] = row[0]
    return rule_dict


def convert_to_rules(param_list):
    rule_dict = get_rule_dict()
    converted_rules = []
    for param in param_list:
        converted_rules.append(rule_dict.get(param))
    return converted_rules


def convert_to_rules_by_rule(param_list, rule_type):
    rule_list = get_rule_list()
    converted_rules = []
    for param in param_list:
        for rule in rule_list:
            if rule[1] == rule_type and rule[2] == param:
                converted_rules.append(int(rule[0]))
    return converted_rules


def get_options(param):
    options = []
    rule_type_dict = get_rule_type_dict()
    rule_list = get_rule_list()
    rule_type = rule_type_dict.get(param)
    for rule in rule_list:
        if rule_type == rule[1]:
            options.append(rule[2])
    return options


def get_schol_list():
    with open(get_secret("VODAFONE_SCHOLARSHIP_FILE")) as data_file:
        file_data = json.load(data_file)
    data = file_data.get("data")
    return data


def get_schol_dict():
    schol_dict = {}
    schol_list = get_schol_list()
    for schol in schol_list:
        schol_dict[schol.get("scholarshipName")] = schol.get("nid")
    return schol_dict


def get_matching_schol(schol):
    schol_dict = get_schol_dict()
    schol_titles = schol_dict.keys()
    matching_schol, score = process.extractOne(schol, schol_titles, scorer=fuzz.partial_token_sort_ratio)
    schol_nid = schol_dict[matching_schol]
    return schol_nid, score


def transform_rules(rules):
    output = []
    rule_list = get_rule_list()
    religion_list = convert_to_rules(get_options("religion"))
    count = 0
    for rule in rules:
        if rule in religion_list:
            count += 1;
    if count == 0:
        for rule in religion_list:
            output.append(rule)
    if "229" in rules:
        for rule in rule_list:
            if rule[1] == "5" and not rule[0] == "229":
                output.append(rule[0])
    for rule in rules:
        if rule not in output:
            output.append(rule)
    return output


def get_schol_rules(schol_id):
    rules = []
    rule_list = []
    schol_list = get_schol_list()
    for schol in schol_list:
        schol_nid = schol.get("nid")
        # print (scholNid)
        if schol_nid == schol_id:
            rules = schol.get("scholarshipRules")
        for rule in rules:
            # print(rule)
            if str(rule.get("rule").get("id")) not in rule_list:
                rule_list.append(str(rule.get("rule").get("id")))
    return rule_list

