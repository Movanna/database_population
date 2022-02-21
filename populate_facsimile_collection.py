# This script populates table publication_facsimile_collection
# and makes the connections to the right publication through
# table publication_facsimile.
# It creates the facsimile folder for each facsimile and fills it
# with the right images, which are renamed, resized and put into
# subdirectories.
#
# The script needs the csv:s which were originally created by the
# find_facsimiles-scripts and later enriched by the
# populate_publication-scripts
# The csv:s contain info about publications and their facsimiles.
#
# Functions create_facsimile_folders and copy_images_to_facs_folders
# borrowed from Niklas Liljestrand (niklil) (who created them for the
# SLS digital publishing platform).

import psycopg2
import re
import os
from shutil import copyfile
from PIL import Image

conn_db = psycopg2.connect(
    host="",
    database="",
    user="",
    port="",
    password=""
)
cursor = conn_db.cursor()

CSV_IN = "csv/Forelasningar_faksimil_id.csv"
# linked printed texts = 0, letters = 1, poems = 2, misc texts = 3, lectures = 4
FACSIMILE_TYPE = "4"
WEB_FACSIMILE_FOLDER = "M:/webbfaksimil/facsimile_collections/"

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
            # get rid of empty value at the end of each list
            # there are two types of csv:s, depending on
            # whether there is an alternative facsimile or not
            print(len(elements))
            if len(elements) == 22:
                elements.pop(21)
            # a list of this length means there will be
            # two separate facsimiles for the publication
            if len(elements) == 23:
                elements.pop(22)
                print("Version coming.")
            list.append(elements)
        return list

def create_publication_facsimile_collection(facsimiles):
    insert_query = """INSERT INTO publication_facsimile_collection(title, number_of_pages, start_page_number, description, folder_path, page_comment, external_url) VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING id"""
    start_page_number = 1
    folder_path = "/facsimiles"
    for facsimile in facsimiles:
        # this is a publication with 1 facsimile
        if len(facsimile) == 21:
            title = facsimile[20]
            description = facsimile[13] + ", " + facsimile[10] + ", " + facsimile[8]
            external_url = facsimile[14]
            publication_id = facsimile[19]
            first_image = facsimile[11]
            last_image = facsimile[12]
            facsimile_paths_orig = facsimile[18]
            facsimile_paths_version = ""
        # this is a publication with 2 separate facsimiles
        if len(facsimile) == 22:
            title = facsimile[21]
            description = facsimile[13] + ", " + facsimile[10] + ", " + facsimile[8]
            external_url = facsimile[14]
            publication_id = facsimile[20]
            first_image = facsimile[11]
            last_image = facsimile[12]
            facsimile_paths_orig = facsimile[18]
            facsimile_paths_version = facsimile[19]
        print(first_image)
        first_image = int(re.sub("^0+", "", first_image))
        last_image = int(re.sub("^0+", "", last_image))
        # number_of_pages in db means number of images
        number_of_pages = last_image - first_image + 1
        if first_image == last_image:
            page_comment = str(first_image)
        else:
            page_comment = str(first_image) + "–" + str(last_image)
        values_to_insert = (title, number_of_pages, start_page_number, description, folder_path, page_comment, external_url)
        cursor.execute(insert_query, values_to_insert)
        facs_coll_id = cursor.fetchone()[0]
        # file paths are a list
        facsimile_paths_orig = re.sub(r"\['|'\]", "", facsimile_paths_orig)
        file_list_orig = facsimile_paths_orig.split("', '")
        create_facsimile_folders(facs_coll_id)
        copy_images_to_facs_folders(file_list_orig, facs_coll_id)
        priority = 1
        create_publication_facsimile(publication_id, facs_coll_id, priority, FACSIMILE_TYPE)
        # add the alternative facsimile
        if facsimile_paths_version != "":
            print("adding version facsimile ...")
            title = "Version / " + facsimile[21]
            first_image = facsimile[16]
            last_image = facsimile[17]
            first_image = int(re.sub("^0+", "", first_image))
            last_image = int(re.sub("^0+", "", last_image))
            # number_of_pages in db means number of images
            number_of_pages = last_image - first_image + 1
            if first_image == last_image:
                page_comment = str(first_image)
            else:
                page_comment = str(first_image) + "–" + str(last_image)
            facsimile_paths_version = re.sub(r"\['|'\]", "", facsimile_paths_version)
            file_list_version = facsimile_paths_version.split("', '")
            values_to_insert = (title, number_of_pages, start_page_number, description, folder_path, page_comment, external_url)
            cursor.execute(insert_query, values_to_insert)
            facs_coll_id = cursor.fetchone()[0]
            facsimile_paths_orig = re.sub(r"\['|'\]", "", facsimile_paths_orig)
            file_list_orig = facsimile_paths_orig.split("', '")
            create_facsimile_folders(facs_coll_id)
            copy_images_to_facs_folders(file_list_version, facs_coll_id)
            priority = 2
            create_publication_facsimile(publication_id, facs_coll_id, priority, FACSIMILE_TYPE)
            print("Version facsimile added.")
    print("Table publication_facsimile_collection updated with new facsimiles.")
    conn_db.commit()

def create_facsimile_folders(facs_coll_id):
    os.makedirs(os.path.dirname(WEB_FACSIMILE_FOLDER + str(facs_coll_id) + "/1/"), exist_ok=True)
    os.makedirs(os.path.dirname(WEB_FACSIMILE_FOLDER + str(facs_coll_id) + "/2/"), exist_ok=True)
    os.makedirs(os.path.dirname(WEB_FACSIMILE_FOLDER + str(facs_coll_id) + "/3/"), exist_ok=True)
    os.makedirs(os.path.dirname(WEB_FACSIMILE_FOLDER + str(facs_coll_id) + "/4/"), exist_ok=True)

def copy_images_to_facs_folders(file_list, facs_coll_id):
    i = 0
    for file in file_list:
        file_number = 1 + i
        print(file + ", " + str(file_number))
        copyfile(str(file), WEB_FACSIMILE_FOLDER + str(facs_coll_id) + "/1/" + str(file_number) + ".jpg")
        image = Image.open(WEB_FACSIMILE_FOLDER + str(facs_coll_id) + "/1/" + str(file_number) + ".jpg")
        resized_im = image.resize((round(image.size[0]*0.5), round(image.size[1]*0.5)))
        resized_im.save(WEB_FACSIMILE_FOLDER + str(facs_coll_id) + "/2/" + str(file_number) + ".jpg", quality=90, optimize=True)
        resized_im = image.resize((round(image.size[0]*0.3), round(image.size[1]*0.3)))
        resized_im.save(WEB_FACSIMILE_FOLDER + str(facs_coll_id) + "/3/" + str(file_number) + ".jpg", quality=90, optimize=True)
        resized_im = image.resize((round(image.size[0]*0.1), round(image.size[1]*0.1)))
        resized_im.save(WEB_FACSIMILE_FOLDER + str(facs_coll_id) + "/4/" + str(file_number) + ".jpg", quality=90, optimize=True)
        i += 1

def create_publication_facsimile(publication_id, facs_coll_id, priority, type):
    page_nr = 0
    section_id = 0
    insert_query = """INSERT INTO publication_facsimile(publication_facsimile_collection_id, publication_id, page_nr, section_id, priority, type) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id"""
    values_to_insert = (facs_coll_id, publication_id, page_nr, section_id, priority, type)
    cursor.execute(insert_query, values_to_insert)

def main():
    facsimiles = create_list_from_csv(CSV_IN)
    create_publication_facsimile_collection(facsimiles)
    conn_db.close()
    cursor.close()

main()