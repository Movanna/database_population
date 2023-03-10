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
# this value is either 0 (unpublished), 1 (internally published)
# or 2 (internally & externally published)
# we want to make tocs either for the internal site (values 1, 2)
# or for the external site (value 2)
# therefore PUBLISHED is always a list, containing either one
# or two values
PUBLISHED = [1, 2]
DELETED = 0
TRANSLATION_TEXT_LANGUAGE = "sv"

# get the relevant info for all publications in a collection
def get_publication_info():
    # toc for the external site
    if len(PUBLISHED) == 1:
        fetch_query = """SELECT publication.id, publication_group_id, published_by, genre, original_publication_date, text, publication.translation_id, field_name FROM publication, translation_text WHERE publication.translation_id = translation_text.translation_id AND (field_name = %s OR field_name = %s) AND table_name = %s AND publication_collection_id = %s AND publication.published = %s AND publication.deleted = %s AND language = %s"""
        values_to_insert = ("name", "subtitle", "publication", COLLECTION_ID, PUBLISHED[0], DELETED, TRANSLATION_TEXT_LANGUAGE)
    # toc for the internal site
    else:
        fetch_query = """SELECT publication.id, publication_group_id, published_by, genre, original_publication_date, text, publication.translation_id, field_name FROM publication, translation_text WHERE publication.translation_id = translation_text.translation_id AND (field_name = %s OR field_name = %s) AND table_name = %s AND publication_collection_id = %s AND (publication.published = %s OR publication.published = %s) AND publication.deleted = %s AND language = %s"""
        values_to_insert = ("name", "subtitle", "publication", COLLECTION_ID, PUBLISHED[0], PUBLISHED[1], DELETED, TRANSLATION_TEXT_LANGUAGE)
    cursor.execute(fetch_query, values_to_insert)
    publication_info = cursor.fetchall()
    # sort the list of tuples according to group, date, id
    # and field_name (the latter two needed for separating subtitles)
    publication_info_sorted = sorted(publication_info, key = operator.itemgetter(1, 4, 0, 7))
    print(len(publication_info_sorted))
    return publication_info_sorted

# toc is a json file i.e. dictionary
def create_dictionary(publication_info_sorted):
    # create top level of dictionary
    toc_dict = {"text": COLLECTION_NAME, "collectionId": str(COLLECTION_ID), "type": "title", "children": []}
    for i in range(len(publication_info_sorted)):
        tuple = publication_info_sorted[i]
        try:
            next_tuple = publication_info_sorted[i + 1]
        except:
            next_tuple = None
        publication_id = tuple[0]
        group = tuple[1]
        published_by = tuple[2]
        genre = tuple[3]
        date = tuple[4]
        publication_title = tuple[5]
        field_name = tuple[7]
        # tuples containing subtitles should not be added
        # as separate toc items, their info belongs to
        # a publication which has already been added
        if field_name == "subtitle":
            continue
        item_id = str(COLLECTION_ID) + "_" + str(publication_id)
        if next_tuple is not None:
            next_field_name = next_tuple[7]
            next_tuple_id = next_tuple[0]
        # first publication or publication whose group_id
        # is different from previous publication's group_id
        # should generate a group level
        # with publications of the same group as children
        if i == 0 or group != publication_info_sorted[i - 1][1]:
            # Finnish group titles are in translation_text
            if TRANSLATION_TEXT_LANGUAGE == "fi":
                fetch_query = """SELECT text FROM translation_text, publication_group WHERE publication_group.translation_id = translation_text.translation_id AND publication_group.id = %s"""
            # Swedish group titles are directly in publication_group
            else:
                fetch_query = """SELECT name FROM publication_group WHERE id = %s"""
            value_to_insert = (group,)
            cursor.execute(fetch_query, value_to_insert)
            group_name = cursor.fetchone()[0]
            toc_midlevel_dict = {"text": group_name, "type": "subtitle", "date": "", "url": "", "children": []}
            toc_dict["children"].append(toc_midlevel_dict)
        # add a description if there is one
        if published_by is not None:
            toc_item_dict = {"url": "", "type": "est", "text": publication_title, "description": published_by, "itemId": item_id, "date": date, "genre": genre}
        # add the subtitle as description if there is one
        # the list has been ordered in such a way that if there's
        # a subtitle to a publication, it should be in the next tuple
        # but we'll check the id to make sure
        elif next_tuple is not None and next_field_name == "subtitle" and publication_id == next_tuple_id:
            subtitle = next_tuple[5]
            toc_item_dict = {"url": "", "type": "est", "text": publication_title, "description": subtitle, "itemId": item_id, "date": date, "genre": genre}
        # these texts should have a differently styled subtitle, 
        # found by splitting the main title into two
        elif publication_title.find("Lantdagen. ") != -1 or publication_title.find("Stadsfullmäktige. ") != -1:   
            publication_title_content = publication_title.split(". ")
            title_one = publication_title_content[0] + "."
            title_two = publication_title_content[1]
            toc_item_dict = {"url": "", "type": "est", "text": title_one, "text_two": title_two, "itemId": item_id, "date": date, "genre": genre}
        # same as above, but for Finnish titles, so there's a possibility
        # of the title containing the abbreviation "n." (circa),
        # which has to be taken into account when splitting
        elif publication_title.find("Valtiopäivät. ") != -1 or publication_title.find("Kaupunginvaltuusto. ") != -1:
            if publication_title.find("n. ") != -1:
                publication_title_content = publication_title.split(". ", 2)
                title_one = publication_title_content[0] + ". " + publication_title_content[1] + "."
                title_two = publication_title_content[2]
                toc_item_dict = {"url": "", "type": "est", "text": title_one, "text_two": title_two, "itemId": item_id, "date": date, "genre": genre}
            else:    
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