# This script populates table publication,
# and also other tables connected to publication, such as
# publication_manuscript, translation, translation_text, event,
# event_connection, event_occurrence. It also creates
# all the needed XML files for each publication and manuscript
# and updates the db with the file paths.

# The starting point is a csv file containing info about
# miscellaneous texts, which will be made into publications.
# This file was updated by one of the find_facsimiles-scripts,
# and this script adds more info to the file:
# the publication id and title. They will be needed later when populating
# table facsimile_collection.

# The script uses dictionaries in order to make genre
# and language values uniform.

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
XML_OUTPUT_FOLDER = "documents/Delutgava_1"
CSV_IN = "csv/mapp_65_faksimil.csv"
CSV_OUT = "csv/mapp_65_faksimil_id.csv"

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
            # get rid of empty value at the end of each list
            print(len(elements))
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

# populate table publication with miscellaneous writings
# and create content in other tables, if needed,
# i.e. translation, translation_text, event, event_connection,
# event_occurrence, publication_manuscript
def create_misc_publication(COLLECTION_ID, misc_publications, genre_dictionary, language_dictionary):
    directory = XML_OUTPUT_FOLDER
    directory_path = create_directory(directory)
    insert_query = """INSERT INTO publication(publication_collection_id, published, genre, original_publication_date, original_language, archive_signum) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id"""
    for publication in misc_publications:
        published = 1
        category = publication[1]
        if category in genre_dictionary.keys():
            genre = genre_dictionary[category]
        else:
            genre = category
        original_date = publication[0]
        original_publication_date, no_date, date_uncertain = replace_date(original_date)
        author = publication[2]
        ms_or_print = publication[3]
        original_title = publication[4]
        language = publication[7]
        # register the language(s)
        original_language, language_for_db = register_language(language, language_dictionary)
        # register the archive signums, old and new
        # and, if present, the folder signum
        # if the document isn't from the National Archives it only has
        # what compares to a folder signum
        old_archive_signum = publication[13]
        new_archive_signum = publication[10]
        archive_folder = publication[8]
        if old_archive_signum is not None and new_archive_signum is not None and archive_folder is not None and archive_folder != "KA":
            archive_signum = old_archive_signum + ", " + new_archive_signum + ", " + archive_folder
        elif old_archive_signum is not None and new_archive_signum is not None and (archive_folder is None or archive_folder == "KA"):
            archive_signum = old_archive_signum + ", " + new_archive_signum
        elif old_archive_signum is None and new_archive_signum is not None and (archive_folder is not None and archive_folder != "KA"):
            archive_signum = new_archive_signum + ", " + archive_folder
        else:
            archive_signum = archive_folder
        values_to_insert = (COLLECTION_ID, published, genre, original_publication_date, language_for_db, archive_signum)
        cursor.execute(insert_query, values_to_insert)
        publication_id = cursor.fetchone()[0]
        # the title of the publication is in swe and fin
        # the titles are kept in a different table, translation_text
        # titles contain the date (almost) as it has been recorded originally
        # translated titles are not yet available so we'll use the Swedish title so far
        title_swe, title_fin, translation_id = add_title(publication_id, original_date, no_date, date_uncertain, original_title)
        # "x" in this column in the original csv means that Mechelin himself
        # is the author of this document
        # Mechelin being the sole author is implicit and not registered in the db
        if author != "x":
            register_author(author, publication_id)
        # if this value is None, it means this publication is a manuscript
        # if value is "t", then this publication is a printed one
        # populate table publication_manuscript if the publication is a ms
        # or if its primary original_language isn't Swedish or Finnish
        if ms_or_print is None or ms_or_print == "m" or (original_language[0] != "sv" and original_language[0] != "fi"):
            # type 1 = letter, 2 = poem, 3 = misc
            manuscript_type = 3
            manuscript_id = create_publication_manuscript(publication_id, published, manuscript_type, archive_signum, language_for_db, title_swe)
        else:
            manuscript_id = None
        # each publication always has two XML-files, a Swedish and a Finnish one
        # if original_language contains something else, then a third file will be created
        # these files contain a template and the editors will fill them with content
        # just like the titles, file paths are not kept in table publication
        # update tables translation_text and publication_manuscript with the file paths
        create_file(directory_path, genre, original_publication_date, original_language, publication_id, translation_id, original_title, title_swe, title_fin, manuscript_id)
        publication.extend((publication_id, title_swe))
        print(publication)
    print("Table publication updated with the new publications.")
    conn_db.commit()
    return misc_publications

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
        match_string_2 = re.search("^ca ", original_date)
        if match_string or match_string_2:
            original_date = original_date.replace("?", "")
            original_date = original_date.replace("ca ", "")
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
        # for cases where original_date was e.g. 18.?.1885
        # and the ? got removed earlier in this function
        if not found:
            search_string = re.compile(r"^(\d{1,2})\.\.(\d{4})")
            match_string = re.search(search_string, original_date)
            if match_string:
                year = match_string.group(2)
                day = match_string.group(1).zfill(2)
                date = year + "-XX-" + day
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
        # for cases where original_date is e.g. "1880-talet"
        # i.e. the 1880s: the year should be recorded as 188X
        if not found:
            search_string = re.compile(r"(\d{3})(\d{1})-tal")
            match_string = re.search(search_string, original_date)
            if match_string:
                date = match_string.group(1)
                date = date + "X-XX-XX"
    if original_date == "" or original_date is None:
        date_uncertain = False
        no_date = True
    return date, no_date, date_uncertain

# there can be several languages for one publication
# meaning that the text e.g. can start off in Swedish
# and then continue in French
# all languages for a publication are recorded in the db
def register_language(language, language_dictionary):
    original_language = []
    if language is None:
        original_language.append("xx")
    else:
        languages = language.split(", ")
        for language in languages:
            if language in language_dictionary.keys():
                language = language_dictionary[language]
                original_language.append(language)
            else:
                original_language.append("xx")
    language_for_db = ", "
    language_for_db = language_for_db.join(original_language)
    return original_language, language_for_db

def register_author(author, publication_id):
    # value None means the author isn't recorded
    # an int value = the subject.id of the author
    # connect the publication to the right person
    # or to the entry for "unknown person"
    # Mechelin being the author is implicit and not registered in the db,
    # unless he's the co-author: then both he and the other one are registered
    # this has been marked in the csv with "/" (+ the subject.id of the co-author)
    # cases where there are more than one co-author are few and will be fixed
    # separately by hand
    LM_is_co_author = False
    if author is None:
        # id for "unknown person"
        subject_id = 1912
    elif "/" in author:
        LM_is_co_author = True
        search_string = re.compile(r"(\d{1,4})$")
        match_string = re.search(search_string, author)
        if match_string:
            subject_id = match_string.group(0)
        else:
            # id for "unknown person"
            subject_id = 1912
    else:
        subject_id = author
    event_connection_type = "wrote misc text"
    event_id = create_event_and_connection(subject_id, LM_is_co_author, event_connection_type)
    # the publication is a misc text
    # so let's register that as explanation for the event_occurrence
    event_occurrence_type = "misc text"
    create_event_occurrence(publication_id, event_id, event_occurrence_type)

# create the titles for the publication
# there's a swe and a fin title
# since the titles haven't been translated yet, we'll just use
# the Swedish title as the Finnish one too, and replace it later
def add_title(publication_id, original_date, no_date, date_uncertain, original_title):
    # make some slight changes to original_date, if needed, since it'll be part of a title
    # if there's some uncertainty about the date, add a standard phrase
    if original_date is not None:
        original_date = original_date.replace("/", ".")
    if no_date is True:
        title_swe = "odaterad " + original_title
        title_fin = "päiväämätön " + original_title
    # if there's some uncertainty about the date, add a standard phrase
    # and leave a "?" only if it signifies "month unknown"
    # also, an "approx." has to be translated, so we can't just use the 
    # Swedish "ca" from the csv as such
    # in the replace_date function we already set the flag
    # which gives the right standard phrases in these cases
    elif date_uncertain is True:
        search_string = re.compile(r"^ca ")
        original_date = search_string.sub("", original_date)
        original_date = original_date.replace("?", "")
        search_string = re.compile(r"\.\.")
        original_date = search_string.sub(".?.", original_date)
        title_swe = "ca " + original_date + " " + original_title
        title_fin = "n. " + original_date + " " + original_title
    else:
        title_swe = original_date + " " + original_title
        title_fin = original_date + " " + original_title
    translation_id = create_translation()
    field_name = "name"
    table_name = "publication"
    create_translation_text(translation_id, title_swe, title_fin, field_name, table_name)
    update_query = """UPDATE publication SET translation_id = %s WHERE id = %s"""
    values_to_insert = (translation_id, publication_id)
    cursor.execute(update_query, values_to_insert)
    return title_swe, title_fin, translation_id

# populate table translation
def create_translation():
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

# create connection between publication and subject (the author of the text)
def create_event_and_connection(subject_id, LM_is_co_author, event_connection_type):
    insert_query = """INSERT INTO event(type) VALUES(%s) RETURNING id"""
    event_type = "published"
    value_to_insert = (event_type,)
    cursor.execute(insert_query, value_to_insert)
    event_id = cursor.fetchone()[0]
    # check if this person exists in the db
    # if not: replace id with id for "unknown person"
    # thus handling e.g. typos in subject_id:s in the csv
    # or a test db with different values than the production db
    fetch_query = """SELECT id FROM subject WHERE id = %s"""
    value_to_insert = (subject_id,)
    cursor.execute(fetch_query, value_to_insert)
    subject_exists = cursor.fetchone()
    if subject_exists is None:
        print("Person with id " + str(subject_id) + " not in db!")
        subject_id = 1912
    insert_query = """INSERT INTO event_connection(subject_id, event_id, type) VALUES(%s, %s, %s)"""
    values_to_insert = (subject_id, event_id, event_connection_type)
    if LM_is_co_author is False:
        cursor.execute(insert_query, values_to_insert)
    # add both Mechelin and the other person as authors
    else:
        cursor.execute(insert_query, values_to_insert)
        # subject.id for Mechelin
        subject_id = 1
        values_to_insert = (subject_id, event_id, event_connection_type)
        cursor.execute(insert_query, values_to_insert)
    return event_id

# create connection between publication and event
def create_event_occurrence(publication_id, event_id, event_occurrence_type):
    insert_query = """INSERT INTO event_occurrence(type, event_id, publication_id) VALUES(%s, %s, %s)"""
    values_to_insert = (event_occurrence_type, event_id, publication_id)
    cursor.execute(insert_query, values_to_insert)

# populate table publication_manuscript
def create_publication_manuscript(publication_id, published, manuscript_type, archive_signum, language_for_db, title_swe):
    insert_query = """INSERT INTO publication_manuscript(publication_id, published, name, type, archive_signum, original_language) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id"""
    values_to_insert = (publication_id, published, title_swe, manuscript_type, archive_signum, language_for_db)
    cursor.execute(insert_query, values_to_insert)
    manuscript_id = cursor.fetchone()[0]
    return manuscript_id

# create a directory
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

# each publication has two XML-files, a Swedish and a Finnish one
# if original_language is something else than sv or fi then
# there's a third file and a file path that goes into publication_manuscript
# otherwise the sv or fi file path goes there (if the publication is a manuscript)
# create files and directories and update translation_text and possibly
# publication_manuscript with file paths
def create_file(directory_path, genre, original_publication_date, original_language, publication_id, translation_id, original_title, title_swe, title_fin, manuscript_id):
    # files and directories contain the publication's date
    original_publication_date = original_publication_date.replace("-", "_")
    title_part = create_title_part_for_file(original_title)
    # make a directory named after the genre (capitalized)
    genre_directory = directory_path + "/" + genre.title()
    genre_directory_path = create_directory(genre_directory)
    final_directory = genre_directory_path + "/" + original_publication_date + "_" + title_part
    final_directory_path = create_directory(final_directory)
    # if the original language is just Swedish or Finnish:
    # there will be two files/file paths for the publication
    # if the publication is a manuscript, the Swedish/Finnish file
    # will be manuscript file
    if original_language[0] == "sv" or original_language[0] == "fi":
        file_name = original_publication_date + "_" + title_part + "_sv_" + str(publication_id) + ".xml"
        file_path_swe = final_directory_path + "/" + file_name
        write_to_file(file_path_swe, title_swe)
        file_name = original_publication_date + "_" + title_part + "_fi_" + str(publication_id) + ".xml"
        file_path_fin = final_directory_path + "/" + file_name
        write_to_file(file_path_fin, title_fin)
        add_file_path(translation_id, file_path_swe, file_path_fin)
        # update publication_manuscript if we're dealing with a manuscript
        if manuscript_id is not None and original_language[0] == "sv":
            update_publication_manuscript_with_file_path(file_path_swe, manuscript_id)
        if manuscript_id is not None and original_language[0] == "fi":
            update_publication_manuscript_with_file_path(file_path_fin, manuscript_id)
    # if the language is foreign:
    # there will be three files/file paths for the publication
    # the foreign file will be manuscript file
    else:
        file_name = original_publication_date + "_" + title_part + "_" + original_language + "_" + str(publication_id) + ".xml"
        file_path_orig = final_directory_path + "/" + file_name
        write_to_file(file_path_orig, title_swe)
        file_name = original_publication_date + "_" + title_part + "_sv_" + str(publication_id) + ".xml"
        file_path_swe = final_directory_path + "/" + file_name
        write_to_file(file_path_swe, title_swe)
        file_name = original_publication_date + "_" + title_part + "_fi_" + str(publication_id) + ".xml"
        file_path_fin = final_directory_path + "/" + file_name
        write_to_file(file_path_fin, title_fin)
        add_file_path(translation_id, file_path_swe, file_path_fin)
        # update publication_manuscript
        update_publication_manuscript_with_file_path(file_path_orig, manuscript_id)

# file and directory names contain the text's title
# with certain replacements
def create_title_part_for_file(original_title):
    title_part = original_title.replace("[...]", "")
    title_part = title_part.replace("[…]", "")
    title_part = title_part.replace("…", "")
    title_part = title_part.replace(". ", "_")
    title_part = title_part.replace(".", "")
    title_part = title_part.replace(" ", "_")
    title_part = title_part.replace("-", "_")
    title_part = title_part.replace("–", "_")
    title_part = title_part.replace("+", "_")
    title_part = title_part.replace("/", "_")
    title_part = re.sub(r",|\?|!|’|»|”|:|;|\(|\)|\[|\]|§|%|\'|\"", "", title_part)
    title_part = title_part.replace("ç", "c")
    title_part = title_part.replace("Ç", "C")
    title_part = title_part.replace("é", "e")
    title_part = title_part.replace("è", "e")
    title_part = title_part.replace("ê", "e")
    title_part = title_part.replace("Ê", "E")
    title_part = title_part.replace("É", "E")
    title_part = title_part.replace("á", "a")
    title_part = title_part.replace("à", "a")
    title_part = title_part.replace("À", "A")
    title_part = title_part.replace("ü", "u")
    title_part = title_part.replace("ú", "u")
    title_part = title_part.replace("Ü", "U")
    title_part = title_part.replace("ï", "i")
    title_part = title_part.replace("í", "i")
    title_part = title_part.replace("ñ", "n")
    title_part = title_part.replace("ô", "o")
    title_part = title_part.replace("ó", "o")
    title_part = title_part.replace("ō", "o")
    title_part = title_part.replace("æ", "ae")
    title_part = title_part.replace("œ", "oe")
    title_part = title_part.replace("ß", "ss")
    title_part = title_part.replace("&", "et")
    title_part = title_part.replace("ø", "o")
    title_part = title_part.replace("Ö", "O")
    title_part = title_part.replace("ö", "o")
    title_part = title_part.replace("Å", "A")
    title_part = title_part.replace("å", "a")
    title_part = title_part.replace("Ä", "A")
    title_part = title_part.replace("ä", "a")
    title_part = title_part.replace("½", "")
    # shorten long names of files and directories
    # otherwise the file path may become too long
    if len(title_part) >= 35:
        title_part = title_part[0:34]
    # if title_part now ends with an underscore:
    # remove that character
    if title_part[-1] == "_":
        title_part = title_part[:-1]
    return title_part

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
        <publisher>Utgåvan Leo Mechelin / Leo Mechelin -editio</publisher>
      </publicationStmt>
      <sourceDesc>
        <p/>
      </sourceDesc>
    </fileDesc>
    </teiHeader>
    <text>
    <body xml:space="preserve">
    <div type="misc">
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
    # info about publications
    misc_publications = create_list_from_csv(CSV_IN)
    genre_dictionary = read_dict_from_file("dictionaries/genre_dictionary.json")
    language_dictionary = read_dict_from_file("dictionaries/language_dictionary.json")
    misc_publications_with_id = create_misc_publication(COLLECTION_ID, misc_publications, genre_dictionary, language_dictionary)
    write_list_to_csv(misc_publications_with_id, CSV_OUT)
    conn_db.close()
    cursor.close()

main()