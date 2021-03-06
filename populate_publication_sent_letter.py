# This script populates table publication,
# and also other tables connected to publication, such as
# publication_manuscript, translation, translation_text, event, event_connection,
# event_occurrence. It also creates all the needed XML files for each
# publication and manuscript and updates the db with the file paths.
#
# The starting point is a csv file containing info about sent letters,
# which will be made into publications. This file was updated by one of the
# find_facsimiles-scripts, and this script adds more info to the file:
# the publication id and title. They will be needed later when populating
# table facsimile_collection.
#
# The script also needs the name_dictionary and the name_id_dictionary
# creted by deal_with_persons.py in order to connect publication with subject
# (in this case a letter and its recipient). It also uses other dictionaries
# in order to make genre and language values uniform, and a csv with
# info about persons.
#
# Sample input and output (CSV) at end of file.

import psycopg2
import re
import os
import json
from bs4 import BeautifulSoup

conn_db = psycopg2.connect(
    host="",
    database="",
    user="",
    port="",
    password=""
)
cursor = conn_db.cursor()

COLLECTION_ID = 1
XML_OUTPUT_FOLDER = "documents/Delutgava_1/Brev/"
CSV_IN = "csv/sent_1_facsimiles.csv"
CSV_OUT = "csv/sent_1_facsimiles_id.csv"

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
            print("list length: " + str(len(elements)))
            # get rid of empty value at the end of each list
            if len(elements) == 20:
                elements.pop(19)
            # if this is the list's length, then there's an alternative facsimile
            if len(elements) == 21:
                elements.pop(20)
        return list

# get dictionary content from file
def read_dict_from_file(filename):
    with open(filename, encoding="utf-8-sig") as source_file:
        json_content = json.load(source_file)
        return json_content

# create a csv file 
def write_list_to_csv(list, filename):
    with open(filename, "w", encoding="utf-8-sig") as output_file:
        for row in list:
            for item in row:
                if item is None:
                    item = ""
                output_file.write(str(item) + ";")
            output_file.write("\n")
    print("List written to file", filename)

# populate table publication with sent letters/telegrams
# and create needed content in other tables, i.e. translation,
# translation_text, event, event_connection, event_occurrence,
# publication_manuscript
def create_sent_publication(COLLECTION_ID, persons_list, sent_letters, name_dictionary, genre_dictionary, language_dictionary, name_id_dictionary):
    directory = XML_OUTPUT_FOLDER + "Sant"
    directory_path = create_directory(directory)
    insert_query = """INSERT INTO publication(publication_collection_id, published, genre, original_publication_date, original_language, archive_signum) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id"""
    for letter in sent_letters:
        published = 1
        category = letter[1]
        # csv is in Finnish, but db has Swedish values for this
        if category in genre_dictionary.keys():
            genre = genre_dictionary[category]
        else:
            genre = category
        original_date = letter[0]
        original_publication_date, no_date, date_uncertain = replace_date(original_date)
        language = letter[7]
        # csv is in Finnish, but db has Swedish values for this
        if language in language_dictionary.keys():
            original_language = language_dictionary[language]
        elif language is None:
            language = "xx"
        else:
            original_language = language
        original_language = original_language.replace("?", "")
        unordered_name = letter[4]
        # register the archive signums, old and new
        # and the folder signum
        archive_signum = letter[13] + ", " + letter[10] + ", " + letter[8]
        values_to_insert = (COLLECTION_ID, published, genre, original_publication_date, original_language, archive_signum)
        cursor.execute(insert_query, values_to_insert)
        publication_id = cursor.fetchone()[0]
        # the title of the publication is in swe and fin
        # the titles are kept in a different table, translation_text
        # titles contain person info
        # titles contain the date (almost) as it has been recorded originally
        person_legacy_id, person, title_swe, title_fin, translation_id = update_sent_publication_with_title(publication_id, unordered_name, persons_list, name_dictionary, original_date, no_date, date_uncertain)
        # these are sent letters/telegrams, i.e. someone else than Mechelin received them
        # update_sent_publication_with_title found out who the receiver was
        # create connection between publication and receiver
        if genre == "s??nt telegram":
            event_connection_type = "received telegram"
        else:
            event_connection_type = "received letter"
        event_id = create_event_and_connection(person_legacy_id, event_connection_type, name_id_dictionary)
        # the publication is still a sent one from Mechelin's point of view
        # so let's register that as well when creating the event_occurrence
        if genre == "s??nt telegram":
            event_occurrence_type = "sent telegram"
        else:
            event_occurrence_type = "sent letter"
        create_event_occurrence(publication_id, event_id, event_occurrence_type)
        # since these publications are manuscripts, populate table publication_manuscript
        manuscript_type = 1
        manuscript_id = create_publication_manuscript(publication_id, published, manuscript_type, archive_signum, original_language, title_swe)
        # each publication always has two XML-files, a Swedish and a Finnish one
        # if original_language is something else, then a third file will be created
        # these files contain a template and the editors will fill them with content
        # just like the titles, file paths are not kept in table publication
        # update tables translation_text and publication_manuscript with the file paths
        create_file(directory_path, person, original_publication_date, original_language, publication_id, translation_id, title_swe, title_fin, manuscript_id)
        letter.extend((publication_id, title_swe))
        print(letter)
    print("Table publication updated with the new publications.")
    conn_db.commit()
    return sent_letters

# date has mainly been recorded as 1.1.1800
# make date format uniform and get rid of other characters
# new format: YYYY-MM-DD, use XX if some part of the date is missing
# if no date can be easily extracted from original_date,
# or if there is no date, make date XXXX-XX-XX
def replace_date(original_date):
    date = "XXXX-XX-XX"
    if original_date is not None:
        original_date = original_date.replace("/", ".")
        original_date = original_date.replace("[", "")
        original_date = original_date.replace("]", "")
        match_string = re.search("\?", original_date)
        if match_string:
            original_date = original_date.replace("?", "")
            date_uncertain = True
        else:
            date_uncertain = False
        no_date = False
        search_string = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})")
        match_string = re.search(search_string, original_date)
        found = False
        if match_string:
            year = match_string.group(3)
            month = match_string.group(2).zfill(2)
            day = match_string.group(1).zfill(2)
            date = year + "-" + month + "-" + day
            found = True
        if not found:
            search_string = re.compile(r"^(\d{1,2})\.(\d{4})")
            match_string = re.search(search_string, original_date)
            if match_string:
                year = match_string.group(2)
                month = match_string.group(1).zfill(2)
                date = year + "-" + month + "-XX"
                found = True
        if not found:
            search_string = re.compile(r"(\d{4})$")
            match_string = re.search(search_string, original_date)
            if match_string:
                date = match_string.group(0)
                date = date + "-XX-XX"
    if original_date == "" or original_date is None:
        date_uncertain = False
        no_date = True
    return date, no_date, date_uncertain

# create the titles for the publication
# it's a sent letter, so the title consists of date, sender and receiver
# there's a swe and a fin title
# due to the nature of the csv we started from, all titles are not going to
# be perfect after this, so some will have to be changed later by hand
# but hey, this is a humanist project
def update_sent_publication_with_title(publication_id, unordered_name, persons_list, name_dictionary, original_date, no_date, date_uncertain):
    # look for person_legacy_id in dictionary using name as key
    if unordered_name in name_dictionary.keys():
        person_legacy_id = name_dictionary[unordered_name]
        title_name_part_swe, title_name_part_fin, person = construct_publication_title_name_part(persons_list, person_legacy_id)
    # if name isn't in dictionary, we don't know this person
    else:
        person_legacy_id = None
        person = None
        title_name_part_swe = "ok??nd"
        title_name_part_fin = "tuntematon"
    # make some slight changes to original_date, if needed, since it'll be part of a title
    # if there's some uncertainty about the date, add a standard phrase
    original_date = original_date.replace("/", ".")
    if no_date is True:
        title_swe = "odaterat" + " LM???" + title_name_part_swe
        title_fin = "p??iv????m??t??n" + " LM???" + title_name_part_fin
    elif date_uncertain is True:
        original_date = original_date.replace("?", "")
        title_swe = "ca " + original_date + " LM???" + title_name_part_swe
        title_fin = "n. " + original_date + " LM???" + title_name_part_fin
    else:
        title_swe = original_date + " LM???" + title_name_part_swe
        title_fin = original_date + " LM???" + title_name_part_fin
    translation_id = create_translation()
    field_name = "name"
    table_name = "publication"
    create_translation_text(translation_id, title_swe, title_fin, field_name, table_name)
    update_query = """UPDATE publication SET translation_id = %s WHERE id = %s"""
    values_to_insert = (translation_id, publication_id)
    cursor.execute(update_query, values_to_insert)
    return person_legacy_id, person, title_swe, title_fin, translation_id

# use person_legacy_id to find out the right person
def construct_publication_title_name_part(persons_list, person_legacy_id):
    for person in persons_list:
        legacy_id = person[13]
        if person_legacy_id == legacy_id:
            title_name_part_swe = construct_swe_name(person)
            title_name_part_fin = construct_fin_name(person, title_name_part_swe)
            break
    return title_name_part_swe, title_name_part_fin, person

# get swe name info for the person chosen
def construct_swe_name(person):
    prefix = person[1]
    surname = person[2]
    forename_letter = person[7]
    if forename_letter and prefix and surname:
        title_name_part_swe = forename_letter + " " + prefix + " " + surname
    elif forename_letter and surname:
        title_name_part_swe = forename_letter + " " + surname
    elif forename_letter:
        title_name_part_swe = forename_letter
    else:
        title_name_part_swe = surname
    return title_name_part_swe

# get fin name info for the person chosen
def construct_fin_name(person, title_name_part_swe):
    prefix = person[1]
    surname = person[2]
    surname_fi = person[3]
    forename_fi = person[4]
    if forename_fi and prefix and surname_fi:
        title_name_part_fin = forename_fi + " " + prefix + " " + surname_fi
    elif forename_fi and prefix:
        title_name_part_fin = forename_fi + " " + prefix + " " + surname
    elif forename_fi and surname_fi:
        title_name_part_fin = forename_fi + " " + surname_fi
    elif forename_fi and surname:
        title_name_part_fin = forename_fi + " " + surname
    elif forename_fi:
        title_name_part_fin = forename_fi
    # there are no cases with only surname_fi, so no need to check for that
    # if there are no Finnish name parts, the Swedish version is to be used
    else:
        title_name_part_fin = title_name_part_swe
    return title_name_part_fin

# populate table translation
def create_translation():
    # translation.neutral_text is there in case text.translation_text has gone missing
    neutral_text = "No translation found"
    insert_query = """INSERT INTO translation(neutral_text) VALUES(%s) RETURNING id"""
    value_to_insert = (neutral_text,)
    cursor.execute(insert_query, value_to_insert)
    translation_id = cursor.fetchone()[0]
    return translation_id

# populate table translation_text with swe and fin titles or file paths
# for the publication
def create_translation_text(translation_id, text_swe, text_fin, field_name, table_name):
    insert_query = """INSERT INTO translation_text(translation_id, language, text, field_name, table_name) VALUES(%s, %s, %s, %s, %s)"""
    values_to_insert_swe = (translation_id, "sv", text_swe, field_name, table_name)
    values_to_insert_fin = (translation_id, "fi", text_fin, field_name, table_name)
    cursor.execute(insert_query, values_to_insert_swe)
    cursor.execute(insert_query, values_to_insert_fin)

# create connection between publication and subject (the receiver of the letter)
def create_event_and_connection(person_legacy_id, event_connection_type, name_id_dictionary):
    insert_query = """INSERT INTO event(type) VALUES(%s) RETURNING id"""
    event_type = "published"
    value_to_insert = (event_type,)
    cursor.execute(insert_query, value_to_insert)
    event_id = cursor.fetchone()[0]
    if person_legacy_id:
        insert_query = """INSERT INTO event_connection(subject_id, event_id, type) VALUES(%s, %s, %s)"""
        subject_id = name_id_dictionary[person_legacy_id]
        subject_id = int(subject_id)
        values_to_insert = (subject_id, event_id, event_connection_type)
    else:
        insert_query = """INSERT INTO event_connection(event_id, type) VALUES(%s, %s)"""
        values_to_insert = (event_id, event_connection_type)
    cursor.execute(insert_query, values_to_insert)
    return event_id

# create connection between publication and event
def create_event_occurrence(publication_id, event_id, event_occurrence_type):
    insert_query = """INSERT INTO event_occurrence(type, event_id, publication_id) VALUES(%s, %s, %s)"""
    values_to_insert = (event_occurrence_type, event_id, publication_id)
    cursor.execute(insert_query, values_to_insert)

# populate table publication_manuscript
def create_publication_manuscript(publication_id, published, manuscript_type, archive_signum, original_language, title_swe):
    insert_query = """INSERT INTO publication_manuscript(publication_id, published, name, type, archive_signum, original_language) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id"""
    values_to_insert = (publication_id, published, title_swe, manuscript_type, archive_signum, original_language)
    cursor.execute(insert_query, values_to_insert)
    manuscript_id = cursor.fetchone()[0]
    return manuscript_id

# create a directory
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

# each publication has two XML files, a Swedish and a Finnish one
# if original_language is something else than sv or fi, then
# there's a third file and a file path that goes into publication_manuscript
# otherwise the sv file path goes there
# create files and directories and update translation_text and
# publication_manuscript with file paths
def create_file(directory_path, person, original_publication_date, original_language, publication_id, translation_id, title_swe, title_fin, manuscript_id):
    # files and directories for letters contain the writer's name 
    if person:
        name_part = create_name_part_for_file(person)
    else:
        name_part = "X_X"
    # files and directories contain the publication's date
    original_publication_date = original_publication_date.replace("-", "_")
    directory = directory_path + "/" + name_part
    person_directory_path = create_directory(directory)
    final_directory = person_directory_path + "/" + original_publication_date + "_" + name_part
    final_directory_path = create_directory(final_directory)
    # if the language is Swedish, then there will be two files/file paths
    # for the publication, and the Swedish file is also manuscript file
    if original_language == "sv":
        file_name = original_publication_date + "_" + name_part + "_" + original_language + "_" + str(publication_id) + ".xml"
        file_path_swe = final_directory_path + "/" + file_name
        write_to_file(file_path_swe, title_swe)
        file_name = original_publication_date + "_" + name_part + "_fi_" + str(publication_id) + ".xml"
        file_path_fin = final_directory_path + "/" + file_name
        write_to_file(file_path_fin, title_fin)
        add_file_path(translation_id, file_path_swe, file_path_fin)
        # update publication_manuscript too
        update_publication_manuscript_with_file_path(file_path_swe, manuscript_id)
    # if the language is foreign, then there will be two files/file paths
    # for the publication, and a foreign manuscript file
    else:
        file_name = original_publication_date + "_" + name_part + "_" + original_language + "_" + str(publication_id) + ".xml"
        file_path_orig = final_directory_path + "/" + file_name
        write_to_file(file_path_orig, title_swe)
        file_name = original_publication_date + "_" + name_part + "_sv_" + str(publication_id) + ".xml"
        file_path_swe = final_directory_path + "/" + file_name
        write_to_file(file_path_swe, title_swe)
        file_name = original_publication_date + "_" + name_part + "_fi_" + str(publication_id) + ".xml"
        file_path_fin = final_directory_path + "/" + file_name
        write_to_file(file_path_fin, title_fin)
        add_file_path(translation_id, file_path_swe, file_path_fin)
        # update publication_manuscript too
        update_publication_manuscript_with_file_path(file_path_orig, manuscript_id)

# file and directory names contain a person's name,
# but not in the same order as in the publication title,
# and with certain replacements
def create_name_part_for_file(person):
    prefix = person[1]
    surname = person[2]
    forename_letter = person[7]
    if forename_letter and prefix and surname:
        name_part = prefix + "_" + surname + "_" + forename_letter
    elif forename_letter and surname:
        name_part = surname + "_" + forename_letter
    elif forename_letter:
        name_part = forename_letter
    else:
        name_part = surname
    name_part = re.sub(r",|\?|!|???|??|???|:|;|\(|\)|\[|\]|\'|\"", "", name_part)
    name_part = name_part.replace(". ", "_")
    name_part = name_part.replace(".", "")
    name_part = name_part.replace(" ", "_")
    name_part = name_part.replace("-", "_")
    name_part = name_part.replace("???", "_")
    name_part = name_part.replace("??", "e")
    name_part = name_part.replace("??", "e")
    name_part = name_part.replace("??", "E")
    name_part = name_part.replace("??", "u")
    name_part = name_part.replace("??", "u")
    name_part = name_part.replace("??", "ae")
    name_part = name_part.replace("&", "et")
    name_part = name_part.replace("??", "o")
    name_part = name_part.replace("??", "O")
    name_part = name_part.replace("??", "o")
    name_part = name_part.replace("??", "A")
    name_part = name_part.replace("??", "a")
    name_part = name_part.replace("??", "A")
    name_part = name_part.replace("??", "a")
    return name_part

# the XML files contain a template with the publication's title
def content_template():
    xml_template = '''
    <TEI xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.tei-c.org/ns/1.0" xsi:schemaLocation="">
    <teiHeader>
    <fileDesc>
      <titleStmt>
        <title></title>
        <respStmt>
          <resp/>
          <name/>
        </respStmt>
      </titleStmt>
      <publicationStmt>
        <publisher>Utg??van Leo Mechelin / Leo Mechelin -editio</publisher>
      </publicationStmt>
      <sourceDesc>
        <p/>
      </sourceDesc>
    </fileDesc>
    </teiHeader>
    <text>
    <body xml:space="preserve">
    <div type="letter">
    </div>
    </body>
    </text>
    </TEI>
    '''
    return BeautifulSoup(xml_template, "xml")

# create the file and its content
def write_to_file(file_path, title):
    with open(file_path, "w", encoding="utf-8-sig") as output_file:
        template_soup = content_template()
        # insert publication name as title
        template_title = template_soup.find("title")
        template_title.append(title)
        # write to file as string
        output_file.write(str(template_soup))

# add file paths to table translation_text
def add_file_path(translation_id, file_path_swe, file_path_fin):
    field_name = "original_filename"
    table_name = "publication"
    create_translation_text(translation_id, file_path_swe, file_path_fin, field_name, table_name)

# update table publication_manuscript
def update_publication_manuscript_with_file_path(file_path, manuscript_id):
    update_query = """UPDATE publication_manuscript SET original_filename = %s WHERE id = %s"""
    values_to_insert = (file_path, manuscript_id)
    cursor.execute(update_query, values_to_insert)

def main():
    persons_list = create_list_from_csv("csv/Personregister.csv")
    # info about publications of type "sent letter"
    sent_letters = create_list_from_csv(CSV_IN)
    name_dictionary = read_dict_from_file("dictionaries/name_dictionary.json")
    genre_dictionary = read_dict_from_file("dictionaries/genre_dictionary.json")
    language_dictionary = read_dict_from_file("dictionaries/language_dictionary.json")
    name_id_dictionary = read_dict_from_file("dictionaries/name_id_dictionary.json")
    sent_letters_with_id = create_sent_publication(COLLECTION_ID, persons_list, sent_letters, name_dictionary, genre_dictionary, language_dictionary, name_id_dictionary)
    write_list_to_csv(sent_letters_with_id, CSV_OUT)
    conn_db.close()
    cursor.close()

main()

'''
sample input:
1873?;l??hetetty kirje;x;;Mechelin, Alexandra;rim;;ruotsi;113 LM/KA;1;1493079741;0395;0395;1886828.KA;;;;;['M:/Faksimiili/Mechelin_4/1493079741/master/0395.jpg'];
sample output:
1873?;l??hetetty kirje;x;;Mechelin, Alexandra;rim;;ruotsi;113 LM/KA;1;1493079741;0395;0395;1886828.KA;;;;;['M:/Faksimiili/Mechelin_4/1493079741/master/0395.jpg'];1749;ca 1873 LM???Alexandra Mechelin;
'''