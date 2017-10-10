import csv

import json

from fuzzywuzzy import process
from nltk.corpus import stopwords

from nltk.tokenize import word_tokenize

from config.settings.base import get_secret


def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    output_text = " ".join(filtered_sentence)
    return output_text


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
    with open(get_secret("SCHOLARSHIPS_JSON_FILE")) as data_file:
        file_data = json.load(data_file)
    body = file_data.get("BODY")
    data = body.get("DATA")
    return data


def get_schol_titles():
    schol_titles = []
    schol_list = get_schol_list()
    for schol in schol_list:
        schol_titles.append(str(schol.get("TITLE")))
    return schol_titles


def get_schol_dict():
    schol_dict = {}
    schol_list = get_schol_list()
    for schol in schol_list:
        schol_dict[schol.get("TITLE")] = schol.get("NID")
    return schol_dict


def get_matching_schol(schol):
    schol_dict = get_schol_dict()
    schol_titles = schol_dict.keys()
    matching_schol = process.extractOne(schol, schol_titles)[0]
    schol_nid = schol_dict[matching_schol]
    return schol_nid
