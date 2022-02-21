# This script populates table subject. The starting point is a csv
# with info about persons, originating from the list constructed
# by sort_persons.py.
# If a person has a different name in Finnish,
# connections are made to tables translation and translation_text. 
#
# The output includes two dictionaries, needed later when populating
# table publication.
#
# Later on, the database schema was changed and translations were
# connected slightly differently. However, the population through
# csv was a one-off forming the backbone of  table subject,
# so there was no need to modify this script once it had fulfilled
# its purpose.

import json
import psycopg2
import re

conn_db = psycopg2.connect(
    host="",
    database="",
    user="",
    port="",
    password=""
)
cursor = conn_db.cursor()

PROJECT_ID = 1

# create a list from the original csv file
# replace empty values with None
def create_list_from_csv(filename):
    with open(filename, "r", encoding="utf-8-sig") as source_file:
        persons_list = []
        for line in source_file:
            row = line.rstrip()
            elements = row.split(";")
            for i in range(0,len(elements)):
                if elements[i] == "":
                    elements[i] = None
            persons_list.append(elements)
        return persons_list

# create a dictionary out of a list
def create_dictionary(list):
    name_dictionary = {}
    for row in list:
        original_name = row[0]
        legacy_id = row[13]
        name_dictionary[original_name] = legacy_id
    return name_dictionary

# save a dictionary as a json file
def write_dict_to_file(dictionary, filename):
    json_dict = json.dumps(dictionary, ensure_ascii=False)
    with open(filename, "w", encoding="utf-8-sig") as output_file:
        output_file.write(json_dict)
        print("Dictionary written to file", filename)

# populate table subject using info from persons_list
# add Finnish names to table translation_text and
# connect them to subject through table translation
# make a dictionary containing old and new person id:s
def create_subject(persons_list, PROJECT_ID):
    insert_query = """INSERT INTO subject(first_name, last_name, preposition, full_name, description, legacy_id, date_born, date_deceased, project_id, alias, previous_last_name, alternative_form, last_name_translation_id, first_name_translation_id, full_name_translation_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"""
    name_id_dictionary = {}
    for person in persons_list:
        prefix = person[1]
        surname = person[2]
        surname_fi = person[3]
        forename_fi = person[4]
        surname_info = person[5]
        alternative_form = person[6]
        forename_short = person[7]
        forename = person[8]
        alias = person[9]
        date_born = person[10]
        date_deceased = person[11]
        description = person[12]
        legacy_id = person[13]
        # the csv and the list made out of it contain multiple entries for
        # the same person; we need that info later when connecting
        # publications to persons, but for table subject we only want
        # one entry for each person, so let's make sure this person
        # isn't already in the table
        select_query = """SELECT id FROM subject WHERE legacy_id = %s"""
        value_to_check = (legacy_id,)
        cursor.execute(select_query, value_to_check)
        query_result = cursor.fetchone()
        if query_result:
            continue
        neutral_text = "No Finnish name found"
        # if there's no forename, the forename info has been recorded in another field
        if forename is None:
            forename = forename_short
        # check for names in Finnish
        if forename_fi or surname_fi:
            full_name_translation_id = construct_full_name_fin(prefix, surname, surname_fi, forename_fi, neutral_text)
        else:
            full_name_translation_id = None
        if forename_fi:
            # replace asterisks, they indicate that a shorter forename exists
            # we don't need to shorten names in Finnish
            forename_fi = forename_fi.replace("*", "")
            first_name_translation_id = create_translation(neutral_text)
            create_translation_text(first_name_translation_id, forename_fi)
        else:
            first_name_translation_id = None
        if surname_fi:
            last_name_translation_id = create_translation(neutral_text)
            create_translation_text(last_name_translation_id, surname_fi)
        else:
            last_name_translation_id = None
        # the entire name with all its parts has to be recorded too
        full_name_swe = construct_full_name_swe(prefix, surname, forename)
        # change date format
        if date_born:
            date_born = replace_date(date_born)
        if date_deceased:
            date_deceased = replace_date(date_deceased)
        # we needed a complete forename for constructing full name, but
        # forename in db should be shorter
        # in the csv an asterisk in the forename field indicated that the
        # person was known under one of his/hers multiple forenames
        # if no asterisk, then we don't know which of the forenames to use
        # so in that case it won't be shortened
        if forename is not None:
            match_string = re.search("\*", forename)
            if match_string:
                forename = forename_short
        values_to_insert = (forename, surname, prefix, full_name_swe, description, legacy_id, date_born, date_deceased, PROJECT_ID, alias, surname_info, alternative_form, last_name_translation_id, first_name_translation_id, full_name_translation_id)
        cursor.execute(insert_query, values_to_insert)
        id = cursor.fetchone()[0]
        name_id_dictionary[legacy_id] = id
        print(person)
    conn_db.commit()
    return name_id_dictionary

def construct_full_name_fin(prefix, surname, surname_fi, forename_fi, neutral_text):
    # there are no cases with surname_fi as the only Finnish name part,
    # so no need to check for that
    if forename_fi and prefix and surname_fi:
        full_name_fin = forename_fi + " " + prefix + " " + surname_fi
    elif forename_fi and prefix:
        full_name_fin = forename_fi + " " + prefix + " " + surname
    elif forename_fi and surname_fi:
        full_name_fin = forename_fi + " " + surname_fi
    elif forename_fi and surname:
        full_name_fin = forename_fi + " " + surname
    # a regent's full name is just the forename, e.g. Victoria
    else:
        full_name_fin = forename_fi
    # replace asterisks, they indicate that a shorter forename exists
    # we need that info later but we don't want asterisks here
    full_name_fin = full_name_fin.replace("*", "")
    translation_id = create_translation(neutral_text)
    create_translation_text(translation_id, full_name_fin)
    return translation_id

def construct_full_name_swe(prefix, surname, forename):
    if forename and prefix and surname:
        full_name_swe = forename + " " + prefix + " " + surname
    elif forename and surname:
        full_name_swe = forename + " " + surname
    elif forename:
        full_name_swe = forename
    elif prefix and surname:
        full_name_swe = prefix + " " + surname
    else:
        full_name_swe = surname
    # replace asterisks, they indicate that a shorter forename exists
    # we need that info later but we don't want asterisks here
    full_name_swe = full_name_swe.replace("*", "")
    return full_name_swe

# populate table translation
def create_translation(neutral_text):
    insert_query = """INSERT INTO translation(neutral_text) VALUES(%s) RETURNING id"""
    value_to_insert = (neutral_text,)
    cursor.execute(insert_query, value_to_insert)
    translation_id = cursor.fetchone()[0]
    return translation_id

# populate table translation_text with Finnish names
def create_translation_text(translation_id, name_fin):
    insert_query = """INSERT INTO translation_text(translation_id, language, text) VALUES(%s, %s, %s)"""
    values_to_insert = (translation_id, "fi", name_fin)
    cursor.execute(insert_query, values_to_insert)

# date has mainly been recorded as 01.01.1800
# make date format uniform 
# new format: YYYY-MM-DD, use XX if some part of the date is missing
# if no date can be easily extracted from original_date, make date XXXX-XX-XX
def replace_date(original_date):
    date = "XXXX-XX-XX"
    search_string = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})")
    match_string = re.search(search_string, original_date)
    if match_string:
        year = match_string.group(3)
        month = match_string.group(2).zfill(2)
        day = match_string.group(1).zfill(2)
        date = year + "-" + month + "-" + day
    search_string = re.compile(r"^(\d{1,2})\.(\d{4})")
    match_string = re.search(search_string, original_date)
    if match_string:
        year = match_string.group(2)
        month = match_string.group(1).zfill(2)
        date = year + "-" + month + "-XX"
    search_string = re.compile(r"(^\d{4})")
    match_string = re.search(search_string, original_date)
    if match_string:
        date = match_string.group(0)
        date = date + "-XX-XX"
    return date

def main():
    persons_list = create_list_from_csv("csv/Personregister.csv")
    name_dictionary = create_dictionary(persons_list)
    write_dict_to_file(name_dictionary, "dictionaries/name_dictionary.json")
    subjects = create_subject(persons_list, PROJECT_ID)
    write_dict_to_file(subjects, "dictionaries/name_id_dictionary.json")
    conn_db.close()
    cursor.close()

main()