# This script adds the connection between translator
# and text, which is kept in table contribution.
# Translators have already been added to table
# contributor, and texts to table publication.
#
# Translators for each text have been registered
# in an Excel-file. The file was simplified
# and then saved as CSV to serve as input for this
# script.
#
# Sample input (CSV) at end of file.

import psycopg2

conn_db = psycopg2.connect(
    host="",
    database="",
    user="",
    port="",
    password=""
)
cursor = conn_db.cursor()

CSV_IN = "csv/translators_and_texts.csv"
CONTRIBUTION_TYPE = "translation"

# create a list from the original csv file
# replace empty values with None
def create_list_from_csv(filename):
    with open(filename, "r", encoding="utf-8-sig") as source_file:
        list = []
        for line in source_file:
            row = line.rstrip()
            elements = row.split(";")
            for i in range(0,len(elements)):
                if elements[i] == "":
                    elements[i] = None
            list.append(elements)
        return list

# sort info and populate table contribution,
# if a translator has been registered for the text
def add_contribution(translation):
    collection_id = translation[0]
    publication_id = translation[1]
    text_language = translation[2]
    translator = translation[4]
    if translator is not None:
        # there might be several translators to a single text
        # registered as Surname_a, Forename_a + Surname_b, Forename_b
        # split the translators and their names and insert
        # each connection separately
        if "+" in translator:
            translators = translator.split(" + ")
            for translator in translators:
                translator = translator.split(", ")
                last_name = translator[0]
                first_name = translator[1]
                contributor_id = fetch_contributor(last_name, first_name)
                if contributor_id is None:
                    print(first_name + " " + last_name + " is not in table contributor!")
                else:
                    create_contribution(collection_id, publication_id, contributor_id, CONTRIBUTION_TYPE, text_language)
        else:
            # split surname and forename
            translator = translator.split(", ")
            last_name = translator[0]
            first_name = translator[1]
            contributor_id = fetch_contributor(last_name, first_name)
            if contributor_id is None:
                print(first_name + " " + last_name + " is not in table contributor!")
            else:
                create_contribution(collection_id, publication_id, contributor_id, CONTRIBUTION_TYPE, text_language)

# fetch id of the contributor from table contributor
def fetch_contributor(last_name, first_name):
    fetch_query = """SELECT id FROM contributor WHERE last_name = %s AND first_name = %s"""
    values_to_insert = (last_name, first_name)
    cursor.execute(fetch_query, values_to_insert)
    translator_id = cursor.fetchone()
    return translator_id

# populate table contribution with connections
# between texts and translators
def create_contribution(collection_id, publication_id, contributor_id, CONTRIBUTION_TYPE, text_language):
    # check whether this translator/text/language combo
    # already is in the db, i.e. has been added earlier
    fetch_query = """SELECT id FROM contribution WHERE publication_id = %s AND contributor_id = %s AND text_language = %s"""
    values_to_insert = (publication_id, contributor_id, text_language)
    cursor.execute(fetch_query, values_to_insert)
    already_exists = cursor.fetchone()
    # only add connection that isn't in db
    if already_exists is None:
        insert_query = """INSERT INTO contribution(publication_collection_id, publication_id, contributor_id, type, text_language) VALUES(%s, %s, %s, %s, %s)"""
        values_to_insert = (collection_id, publication_id, contributor_id, CONTRIBUTION_TYPE, text_language)
        cursor.execute(insert_query, values_to_insert)

def main():
    translated_publications = create_list_from_csv(CSV_IN)
    for translation in translated_publications:
        add_contribution(translation)
    conn_db.commit()
    print("Translations added to table contribution.")
    conn_db.close()
    cursor.close()

main()

'''
sample input:
1;106;fi;fr;Surname, Forename
'''