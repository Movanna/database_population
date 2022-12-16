# This script populates table publication,
# and also two other tables connected to publication:
# translation and translation_text. It also creates all 
# the needed XML files for each publication and
# updates the db with the file paths.

# The starting point is a csv file containing info about hansards,
# which will be made into publications. This script adds more info
# to the file: the publication id and title. They are needed later
# when populating table facsimile_collection.
#
# Sample input and output (CSV) at end of file.

import psycopg2
import re
import os
from bs4 import BeautifulSoup

conn_db = psycopg2.connect(
    host="",
    database="",
    user="",
    port="",
    password=""
)
cursor = conn_db.cursor()

# input the parameters for the hansards
COLLECTION_ID = 1
XML_OUTPUT_FOLDER = "documents/Delutgava_1/Lantdagen"
GENRE = "lantdagsprotokoll"
CSV_IN = "csv/lantdagen_1.csv"
CSV_OUT = "csv/lantdagen_1_id.csv"

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

# populate table publication with hansards and create needed content
# in other tables, i.e. translation, translation_text
def create_hansard_publication(hansards):
    directory = XML_OUTPUT_FOLDER
    directory_path = create_directory(directory)
    insert_query = """INSERT INTO publication(publication_collection_id, published, genre, original_publication_date, original_language) VALUES(%s, %s, %s, %s, %s) RETURNING id"""
    for hansard in hansards:
        published = 1
        original_date = hansard[0]
        original_publication_date, date_uncertain, year = replace_date(original_date)
        # all of the hansards are in Swedish
        original_language = "sv"
        original_title = hansard[1]
        values_to_insert = (COLLECTION_ID, published, GENRE, original_publication_date, original_language)
        cursor.execute(insert_query, values_to_insert)
        publication_id = cursor.fetchone()[0]
        # the title of the publication is in swe and fin
        # the titles are kept in a different table
        # title contains the date as it has been recorded originally
        # translated titles are not yet available so we'll use the Swedish title so far
        title_swe, title_fin, translation_id = add_title(publication_id, original_date, date_uncertain, original_title)
        # each publication has two XML-files, a Swedish and a Finnish one
        # these files contain a template and the editors will fill them with content
        # update table translation_text with the file paths
        create_file(directory_path, original_publication_date, year, original_language, publication_id, translation_id, original_title, title_swe)
        hansard.extend((publication_id, title_swe))
        print(hansard)
    print("Table publication updated with the new publications.")
    conn_db.commit()
    return hansards

# date has mainly been recorded as 1.1.1800
# make date format uniform and get rid of other characters
# new format: YYYY-MM-DD, use XX if some part of the date is missing
# if no date can be easily extracted from original_date, make date XXXX-XX-XX
def replace_date(original_date):
    date = "XXXX-XX-XX"
    original_date = original_date.replace("/", ".")
    original_date = original_date.replace("[", "")
    original_date = original_date.replace("]", "")
    match_string = re.search("\?", original_date)
    if match_string:
        original_date = original_date.replace("?", "")
        date_uncertain = True
    else:
        date_uncertain = False
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
    return date, date_uncertain, year

# create the titles for the publication
# there's a swe and a fin title
# since the titles haven't been translated yet, we'll just use
# the Swedish title as the Finnish one too, and replace it later
def add_title(publication_id, original_date, date_uncertain, original_title):
    # make some slight changes to original_date, if needed, since it'll be part of a title
    # if there's some uncertainty about the date, add a standard phrase
    original_date = original_date.replace("/", ".")
    if date_uncertain is True:
        original_date = original_date.replace("?", "")
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

# create a directory
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

# each publication has two XML files, a Swedish and a Finnish one
# create files and directories
# and update table translation_text with the file paths
def create_file(directory_path, original_publication_date, year, original_language, publication_id, translation_id, original_title, title_swe):
    # files and directories contain the publication's date
    original_publication_date = original_publication_date.replace("-", "_")
    directory = directory_path + "/" + year
    year_directory_path = create_directory(directory)
    title_part = create_title_part_for_file(original_title)
    final_directory = year_directory_path + "/" + original_publication_date + "_" + title_part
    final_directory_path = create_directory(final_directory)
    # since the original language is Swedish there will be two files/file paths
    # for the publication
    file_name = original_publication_date + "_" + title_part + "_" + original_language + "_" + str(publication_id) + ".xml"
    file_path_swe = final_directory_path + "/" + file_name
    write_to_file(file_path_swe, title_swe)
    file_name = original_publication_date + "_" + title_part + "_fi_" + str(publication_id) + ".xml"
    file_path_fin = final_directory_path + "/" + file_name
    write_to_file(file_path_fin, title_swe)
    add_file_path(translation_id, file_path_swe, file_path_fin)

# file and directory names contain the hansard's title
# with certain replacements
def create_title_part_for_file(title_part):
    title_part = title_part.replace(". ", "_")
    title_part = title_part.replace(".", "")
    title_part = title_part.replace(" ", "_")
    title_part = title_part.replace("-", "_")
    title_part = title_part.replace("–", "_")
    title_part = re.sub(r",|\?|!|’|»|”|:|;|\(|\)|\[|\]|\'|\"", "", title_part)
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
    title_part = title_part.replace("ô", "o")
    title_part = title_part.replace("ó", "o")
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
    # shorten long names of files and directories
    # otherwise the file path may become too long
    if len(title_part) >= 45:
        title_part = title_part[0:44]
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
    <div type="hansard">
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

def main():
    # info about publications of type "hansard"
    hansards = create_list_from_csv(CSV_IN)
    hansards_with_id = create_hansard_publication(hansards)
    write_list_to_csv(hansards_with_id, CSV_OUT)
    conn_db.close()
    cursor.close()

main()

'''
sample input:
28.3.1877;Lantdagen. Allmän värnplikt
sample output:
28.3.1877;Lantdagen. Allmän värnplikt;1748;28.3.1877 Lantdagen. Allmän värnplikt;
'''
