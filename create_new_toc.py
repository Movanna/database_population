# This script generates a table of contents file (toc) for 
# the website, as json. The toc is the side menu of the site.
# There is a Swedish and a Finnish toc, and they contain 
# all publications belonging to a collection sorted as follows:
# firstly according to the publications' group id
# and then chronologically within the group. The toc displays
# the publication's title and possible descriptions, and
# on the site it can be sorted according to genre and date. 

# The script fetches publication data from the db and also
# checks all the files belonging to each publication in order to
# determine whether this publication has text content or not.
# In this project, a publication consists either of images 
# and metadata, or of text, metadata and (usually) images.
# The two cases are styled differently in the side menu depending
# on their content value.

# The script also replaces unknown dates with the latest possible date,
# so that the toc sorting options on the site can work properly.
# Also: a publication may belong to multiple genres, but the sort
# options on the site only work with one genre value, so if there
# are several values, the first one is chosen for the toc.

# Sample output (JSON) at end of file.

import psycopg2
from pathlib import Path
from bs4 import BeautifulSoup
import re
import json

conn_db = psycopg2.connect(
    host="",
    database="",
    user="",
    port="",
    password=""
)
cursor = conn_db.cursor()

# set different parameters for what to include in the toc file
COLLECTION_ID = 1
# this value is either 0 (unpublished), 1 (internally published)
# or 2 (internally & externally published)
# we want to make tocs either for the internal site (values 1, 2)
# or for the external site (value 2)
# therefore PUBLISHED is always a list, containing either one
# or two values
PUBLISHED = [1, 2]
DELETED = 0
TRANSLATION_TEXT_LANGUAGE = ["sv", "fi"]
SOURCE_FOLDER = "../GitHub/leomechelin_files/"

# get the relevant info for all publications in a collection
def get_publication_info():
    # the query initially returns 4-6 tuples per publication id:
    # merge these into 1 single tuple using GROUP BY and MAX
    # then order the tuples by publication group and date
    # one PUBLISHED value is the toc for the external site
    if len(PUBLISHED) == 1:
        fetch_query = """SELECT publication.id, publication_group_id, publication.published_by, genre, original_publication_date, publication_manuscript.original_filename,
        MAX(CASE
            WHEN translation_text.language = 'sv' AND translation_text.field_name = 'name' THEN translation_text.text
        END) AS "title_sv",
        MAX(CASE
            WHEN translation_text.language = 'fi' AND translation_text.field_name = 'name' THEN translation_text.text
        END) AS "title_fi",
        MAX(CASE
            WHEN translation_text.language = 'sv' AND translation_text.field_name = 'subtitle' THEN translation_text.text
        END) AS "subtitle_sv",
        MAX(CASE
            WHEN translation_text.language = 'fi' AND translation_text.field_name = 'subtitle' THEN translation_text.text
        END) AS "subtitle_fi",
        MAX(CASE
            WHEN translation_text.language = 'sv' AND translation_text.field_name = 'original_filename' THEN translation_text.text
        END) AS "filename_sv",
        MAX(CASE
            WHEN translation_text.language = 'fi' AND translation_text.field_name = 'original_filename' THEN translation_text.text
        END) AS "filename_fi"
        FROM publication
        LEFT JOIN translation_text ON publication.translation_id = translation_text.translation_id
        LEFT JOIN publication_manuscript ON publication.id = publication_manuscript.publication_id
        WHERE publication_collection_id = %s AND publication.published = %s AND publication.deleted = %s AND translation_text.deleted = %s AND (publication_manuscript.deleted = %s OR publication_manuscript.deleted IS NULL)
        GROUP BY publication.id, publication_manuscript.original_filename
        ORDER BY publication_group_id, original_publication_date, publication.id"""
        values_to_insert = (COLLECTION_ID, PUBLISHED[0], DELETED, DELETED, DELETED)
    # this is toc for the internal site
    else:
        fetch_query = """SELECT publication.id, publication_group_id, publication.published_by, genre, original_publication_date, publication_manuscript.original_filename,
        MAX(CASE
            WHEN translation_text.language = 'sv' AND translation_text.field_name = 'name' THEN translation_text.text
        END) AS "title_sv",
        MAX(CASE
            WHEN translation_text.language = 'fi' AND translation_text.field_name = 'name' THEN translation_text.text
        END) AS "title_fi",
        MAX(CASE
            WHEN translation_text.language = 'sv' AND translation_text.field_name = 'subtitle' THEN translation_text.text
        END) AS "subtitle_sv",
        MAX(CASE
            WHEN translation_text.language = 'fi' AND translation_text.field_name = 'subtitle' THEN translation_text.text
        END) AS "subtitle_fi",
        MAX(CASE
            WHEN translation_text.language = 'sv' AND translation_text.field_name = 'original_filename' THEN translation_text.text
        END) AS "filename_sv",
        MAX(CASE
            WHEN translation_text.language = 'fi' AND translation_text.field_name = 'original_filename' THEN translation_text.text
        END) AS "filename_fi"
        FROM publication
        LEFT JOIN translation_text ON publication.translation_id = translation_text.translation_id
        LEFT JOIN publication_manuscript ON publication.id = publication_manuscript.publication_id
        WHERE publication_collection_id = %s AND (publication.published = %s or publication.published = %s) AND publication.deleted = %s AND translation_text.deleted = %s AND (publication_manuscript.deleted = %s OR publication_manuscript.deleted IS NULL)
        GROUP BY publication.id, publication_manuscript.original_filename
        ORDER BY publication_group_id, original_publication_date, publication.id"""        
        values_to_insert = (COLLECTION_ID, PUBLISHED[0], PUBLISHED[1], DELETED, DELETED, DELETED)
    cursor.execute(fetch_query, values_to_insert)
    publication_info_sorted = cursor.fetchall()
    print(len(publication_info_sorted))
    return publication_info_sorted

# a publication has 2 or 3 files depending on its language
# and text type (manuscript/printed)
# there are always sv and fi files
# get the files checked for text content
# we need to know whether this publication has content 
# in any of its files or not
def get_content(publication_info_sorted):
    publication_info_with_content = []
    for publication in publication_info_sorted:
        filepath_sv = Path(SOURCE_FOLDER + publication[10])
        filepath_fi = Path(SOURCE_FOLDER + publication[11])
        original_filepath = publication[5]
        # always check sv and fi files
        # if the manuscript file is the same as the sv or fi file:
        # the file will have been checked already, don't check it 
        # again separately
        if original_filepath == filepath_sv or original_filepath == filepath_fi:
            original_filepath = None
        if original_filepath is not None:
            original_filepath = Path(SOURCE_FOLDER + publication[5])
        files = [filepath_sv, filepath_fi, original_filepath]
        content = check_xml_content(files)
        content = tuple((content,))
        # add the content value (True/False) to the existing tuple
        publication += content
        # add the updated tuples to the new list
        publication_info_with_content.append(publication)
    print("Publications checked for content.")
    return publication_info_with_content

# read an xml file and return its content as a soup object
# strip newlines (otherwise they'll get counted as characters)
# and use space to join the text contents of all the elements
# we don't need to know the exact content length,
# just whether there is any text content or not, apart from
# the template, which is always present in the files
def check_xml_content(files):
    content = False
    for file in files:
        if file is None:
            continue
        else:
            with file.open("r", encoding="utf-8-sig") as source_file:
                file_content = source_file.read()
                xml_soup = BeautifulSoup(file_content, "xml")
            main_div = xml_soup.body.div
            if len(main_div.get_text(strip = True)) == 0:
                continue
            else:
                content = True
    return content

# get dictionary content from file
def read_dict_from_file(filename):
    with open(filename, encoding="utf-8-sig") as source_file:
        json_content = json.load(source_file)
        return json_content

# toc is a json file i.e. a dictionary
# top level: collection name, mid level: group name, then the publication titles
def create_toc(publication_info_with_content, toc_language, genre_dictionary):
    # create the top level of the dictionary, i.e. the collection name
    fetch_query = """SELECT name, text FROM publication_collection, translation_text WHERE publication_collection.translation_id = translation_text.translation_id AND publication_collection.id = %s"""
    value_to_insert = (COLLECTION_ID,)
    cursor.execute(fetch_query, value_to_insert)
    collection_names = cursor.fetchone()
    if toc_language == "sv":
        toc_dict = {"text": collection_names[0], "collectionId": str(COLLECTION_ID), "type": "title", "children": []}
    else:
        toc_dict = {"text": collection_names[1], "collectionId": str(COLLECTION_ID), "type": "title", "children": []}
    for i in range(len(publication_info_with_content)):
        publication = publication_info_with_content[i]
        publication_id = publication[0]
        group = publication[1]
        published_by = publication[2]
        genre_sv = publication[3]
        original_date = publication[4]
        title_sv = publication[6]
        title_fi = publication[7]
        subtitle_sv = publication[8]
        subtitle_fi = publication[9]
        content = publication[12]
        if toc_language == "sv":
            title = title_sv
            subtitle = subtitle_sv
        else:
            title = title_fi
            subtitle = subtitle_fi
        item_id = str(COLLECTION_ID) + "_" + str(publication_id)
        # dates can contain uncertainty in the db, but the website
        # needs actual dates for the sorting of the toc
        # replace uncertain dates with the latest possible date
        if "X" in original_date:
            date = fix_date(original_date, COLLECTION_ID)
        else:
            date = original_date
        # a publication may belong to multiple genres, but the sort
        # options on the site only work with one genre value
        # also, genre in db is in Swedish and needs translation for fi toc
        # and the genre value should be capitalized since it appears
        # in the toc as the name of a group level
        genre = fix_genre(toc_language, genre_sv, genre_dictionary)
        # the first publication or a publication whose group_id
        # is different from previous publication's group_id
        # should generate a group level
        # with publications belonging to the same group as children
        if i == 0 or group != publication_info_with_content[i - 1][1]:
            # Finnish group titles are in translation_text
            if toc_language == "fi":
                fetch_query = """SELECT text FROM translation_text, publication_group WHERE publication_group.translation_id = translation_text.translation_id AND publication_group.id = %s"""
            # Swedish group titles are directly in publication_group
            else:
                fetch_query = """SELECT name FROM publication_group WHERE id = %s"""
            value_to_insert = (group,)
            cursor.execute(fetch_query, value_to_insert)
            group_name = cursor.fetchone()[0]
            toc_midlevel_dict = {"text": group_name, "type": "subtitle", "children": []}
            toc_dict["children"].append(toc_midlevel_dict)
        # add the subtitle/publisher
        if published_by is not None and subtitle is not None:
            toc_item_dict = {"type": "est", "text": title, "subtitle": subtitle, "description": published_by, "itemId": item_id, "date": date, "genre": genre}
        elif published_by is not None and subtitle is None:
            toc_item_dict = {"type": "est", "text": title, "description": published_by, "itemId": item_id, "date": date, "genre": genre}
        elif published_by is None and subtitle is not None:
            toc_item_dict = {"type": "est", "text": title, "subtitle": subtitle, "itemId": item_id, "date": date, "genre": genre}
        # these texts should have a different kind of subtitle, 
        # found by splitting the main title into two
        elif title.find("Lantdagen. ") != -1 or title.find("Stadsfullmäktige. ") != -1:   
            title_content = title.split(". ")
            title_one = title_content[0] + "."
            title_two = title_content[1]
            toc_item_dict = {"type": "est", "text": title_one, "text_two": title_two, "itemId": item_id, "date": date, "genre": genre}
        # same as above, but for Finnish titles, so there's a possibility
        # of the title containing the abbreviation "n." (circa),
        # which has to be taken into account when splitting
        elif title.find("Valtiopäivät. ") != -1 or title.find("Kaupunginvaltuusto. ") != -1:
            if title.find("n. ") != -1:
                title_content = title.split(". ", 2)
                title_one = title_content[0] + ". " + title_content[1] + "."
                title_two = title_content[2]
                toc_item_dict = {"type": "est", "text": title_one, "text_two": title_two, "itemId": item_id, "date": date, "genre": genre}
            else:    
                title_content = title.split(". ")
                title_one = title_content[0] + "."
                title_two = title_content[1]
                toc_item_dict = {"type": "est", "text": title_one, "text_two": title_two, "itemId": item_id, "date": date, "genre": genre}
        else:
            toc_item_dict = {"type": "est", "text": title, "itemId": item_id, "date": date, "genre": genre}
        # depending on content value, this publication either
        # consists only of images and metadata, or of text, metadata
        # and (usually) images
        if content is True:
            toc_item_dict.update({"facsimileOnly": False})
        else:
            toc_item_dict.update({"facsimileOnly": True})
        toc_midlevel_dict["children"].append(toc_item_dict)
    return toc_dict

# the toc can be sorted by date on the website
# for this the date can't contain X, which it can in the db
# replace all unknown dates with their latest possible date
# e.g. 188X with 1889
def fix_date(original_date, COLLECTION_ID):
    # if there's no date at all, use the latest possible date
    # of the collection
    if original_date == "XXXX-XX-XX":
        if COLLECTION_ID == 1:
            date = "1872-12-31"
        elif COLLECTION_ID == 2:
            date = "1881-12-31"
        elif COLLECTION_ID == 3:
            date = "1890-06-30"
        elif COLLECTION_ID == 4:
            date = "1898-07-31"
        elif COLLECTION_ID == 5:
            date = "1903-03-31"
        elif COLLECTION_ID == 6:
            date = "1905-11-30"
        elif COLLECTION_ID == 7:
            date = "1908-06-30"
        elif COLLECTION_ID == 8:
            date = "1910-06-30"
        else:
            date = "1914-12-31"
    else:
        search_string = re.compile(r"(.{4})-(.{2})-(.{2})")
        match_string = re.search(search_string, original_date)
        if match_string:
            year = match_string.group(1)
            month = match_string.group(2)
            day = match_string.group(3)
            if "X" in year:
                # 1914 is the latest possible year in this project
                if year == "19XX" or year == "1XXX":
                    year = "1914"
                else:
                    year = year.replace("X", "9")
            # uncertain months and days have only been recorded as XX
            # not as e.g. 1X or X2
            if "X" in month:
                month = "12"
            if "X" in day:
                if month == "11" or month == "04" or month == "06"or month == "09":
                    day = "30"
                elif month == "02":
                    day = "28"
                else:
                    day = "31"
        date = year + "-" + month + "-" + day
    return date

# genre in db is in Swedish and needs translation for fi toc
# also: use only the first genre value if there are multiple values
# and capitalize the genre value
def fix_genre(toc_language, genre_sv, genre_dictionary):
    # use only the first of multiple genre values
    if "," in genre_sv:
        genres = genre_sv.split(", ")
        genre = genres[0].capitalize()
        # genre in db is in Swedish, check dictionary for translation
        if toc_language == "fi":
            if genre in genre_dictionary.keys():
                genre = genre_dictionary[genre].capitalize()
    # if toc_language is fi and there's a single genre value
    elif toc_language == "fi":
        if genre_sv in genre_dictionary.keys():
            genre = genre_dictionary[genre_sv].capitalize()
        else:
            genre = genre_sv.capitalize()
    else:
        genre = genre_sv.capitalize()
    return genre

# save toc/dictionary as file
def write_dict_to_file(dictionary, filename):
    json_dict = json.dumps(dictionary, ensure_ascii=False)
    with open(filename, "w", encoding="utf-8") as output_file:
        output_file.write(json_dict)
        print("Dictionary written to file", filename)

def main():
    # get all publications for the chosen collection
    publication_info_sorted = get_publication_info()
    # check whether the publications have text content or not
    publication_info_with_content = get_content(publication_info_sorted)
    # genre value translations
    genre_dictionary = read_dict_from_file("dictionaries/new_genre_dictionary.json")
    # create a sv and a fi toc file
    for toc_language in TRANSLATION_TEXT_LANGUAGE:
        toc_dict = create_toc(publication_info_with_content, toc_language, genre_dictionary)
        filename = "json/" + str(COLLECTION_ID) + "_" + toc_language + ".json"
        write_dict_to_file(toc_dict, filename)
    conn_db.close()
    cursor.close()

main()

'''
A sample extract from a toc file:
{
    "text": "1873–1881: Läran om staten – Professorsåren",
    "collectionId": "2",
    "type": "title",
    "children": [
        {
            "text": "1873: Meritering",
            "type": "subtitle",
            "children": [
                {
                    "type": "est",
                    "text": "1.1.1873 Torsten & Jenny Costiander–LM",
                    "itemId": "2_3250",
                    "date": "1873-01-01",
                    "genre": "Mottaget brev",
                    "facsimileOnly": false
                },
                {
                    "type": "est",
                    "text": "14.7.1873 Tal vid C. Ehrnroots jordfästning",
                    "description": "Helsingfors Dagblad 14.7.1873",
                    "itemId": "2_2016",
                    "date": "1873-07-14",
                    "genre": "Artikel",
                    "facsimileOnly": false
                }
            ]
        },
        {
            "text": "1874–1876: Professor och adelsman",
            "type": "subtitle",
            "children": [
                {
                    "type": "est",
                    "text": "23.2.1874 Professor i kameral- och politilagfarenhet samt statsrätt",
                    "itemId": "2_4256",
                    "date": "1874-02-23",
                    "genre": "Diplom",
                    "facsimileOnly": true
                },
                {
                    "type": "est",
                    "text": "21.2.1876 Finanslära",
                    "subtitle": "föreläsning 9",
                    "itemId": "2_1467",
                    "date": "1876-02-21",
                    "genre": "Föreläsning",
                    "facsimileOnly": true
                }
            ]
        }
    ]
}
'''