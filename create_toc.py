# This script generates a table of contents file (toc) as json
# containing all publications belonging to a collection
# and sorted as follows:
# firstly according to the publications' group id
# and then chronologically within the group.

import psycopg2
import operator
import json

conn_db = psycopg2.connect(
    host="",
    database="",
    user="",
    port="",
    password=""
)
cursor = conn_db.cursor()

# set different parameters for what to include
# in the toc file
COLLECTION_ID = 1
COLLECTION_NAME = "delutgåva 1"
PUBLISHED = 1
DELETED = 0
TRANSLATION_TEXT_LANGUAGE = "sv"

# get the relevant info for all publications in a collection
def get_publication_info():
    fetch_query = """SELECT publication.id, publication_group_id, published_by, genre, original_publication_date, text, publication.translation_id FROM publication, translation_text WHERE publication.translation_id = translation_text.translation_id AND field_name = %s AND table_name = %s AND publication_collection_id = %s AND publication.published = %s AND publication.deleted = %s AND language = %s"""
    values_to_insert = ("name", "publication", COLLECTION_ID, PUBLISHED, DELETED, TRANSLATION_TEXT_LANGUAGE)
    cursor.execute(fetch_query, values_to_insert)
    publication_info = cursor.fetchall()
    publication_info_sorted = sorted(publication_info, key = operator.itemgetter(1, 4))
    print(len(publication_info_sorted))
    return publication_info_sorted

# toc is a json file i.e. dictionary
def create_dictionary(publication_info_sorted):
    # create top level of dictionary
    toc_dict = {"text": COLLECTION_NAME, "collectionId": str(COLLECTION_ID), "type": "title", "children": []}
    for i in range(len(publication_info_sorted)):
        row = publication_info_sorted[i]
        publication_id = row[0]
        group = row[1]
        published_by = row[2]
        genre = row[3]
        date = row[4]
        publication_title = row[5]
        translation_id = row[6]
        item_id = str(COLLECTION_ID) + "_" + str(publication_id)
        # fetch subtitle if the publication is a lecture
        if genre == "föreläsning":
            field_name = "subtitle"
            fetch_query = """SELECT text FROM translation_text WHERE translation_id = %s AND field_name = %s AND language = %s"""
            values_to_insert = (translation_id, field_name, TRANSLATION_TEXT_LANGUAGE)
            cursor.execute(fetch_query, values_to_insert)
            subtitle = cursor.fetchone()[0]
        # first publication or publication whose group_id
        # is different from previous publication's group_id
        # should generate a group level
        # with publications of the same group as children
        if i == 0 or group != publication_info_sorted[i-1][1]:
            fetch_query = """SELECT name FROM publication_group WHERE id = %s"""
            value_to_insert = (group,)
            cursor.execute(fetch_query, value_to_insert)
            group_name = cursor.fetchone()[0]
            toc_midlevel_dict = {"text": group_name, "type": "subtitle", "date": "", "url": "", "children": []}
            toc_dict["children"].append(toc_midlevel_dict)
        # add a description if there is one
        if published_by is not None:
            toc_item_dict = {"url": "", "type": "est", "text": publication_title, "description": published_by, "itemId": item_id, "date": date, "genre": genre}
        # add the subtitle as description if the publication is a lecture
        elif genre == "föreläsning":
            toc_item_dict = {"url": "", "type": "est", "text": publication_title, "description": subtitle, "itemId": item_id, "date": date, "genre": genre}
        # these texts should have a differently styled title in toc
        elif publication_title.find("Lantdagen. ") != -1:
            publication_title_content = publication_title.split(". ")
            title_one = publication_title_content[0] + "."
            title_two = publication_title_content[1]
            toc_item_dict = {"url": "", "type": "est", "text": title_one, "text_two": title_two, "itemId": item_id, "date": date, "genre": genre}
        else:
            toc_item_dict = {"url": "", "type": "est", "text": publication_title, "itemId": item_id, "date": date, "genre": genre}
        toc_midlevel_dict["children"].append(toc_item_dict)
    return toc_dict

# save dictionary as file
def write_dict_to_file(dictionary, filename):
    json_dict = json.dumps(dictionary, ensure_ascii=False)
    with open(filename, "w", encoding="utf-8") as output_file:
        output_file.write(json_dict)
        print("Dictionary written to file", filename)

def main():
    publication_info_sorted = get_publication_info()
    toc_dict = create_dictionary(publication_info_sorted)
    if TRANSLATION_TEXT_LANGUAGE == "fi":
        filename = "json/" + str(COLLECTION_ID) + "_fi" + ".json"
    else:
        filename = "json/" + str(COLLECTION_ID) + "_sv" + ".json"
    write_dict_to_file(toc_dict, filename)
    conn_db.close()
    cursor.close()

main()
