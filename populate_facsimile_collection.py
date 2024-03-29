# This script populates table publication_facsimile_collection
# and makes the connections to the right publication through
# table publication_facsimile.
# It creates the facsimile folder for each facsimile as well as
# the required subdirectory, which is then filled with the renamed images.

# The script needs the csv:s which were originally created by the
# find_facsimiles-scripts and later enriched by the
# populate_publication-scripts
# The csv:s contain info about publications and their facsimiles.

# Sample input (CSV) at end of file.

import psycopg2
import re
import os
from shutil import copyfile

conn_db = psycopg2.connect(
    host="",
    database="",
    user="",
    port="",
    password=""
)
cursor = conn_db.cursor()

CSV_IN = "csv/Forelasningar_faksimil_id.csv"
# linked printed texts = 0, letters = 1, poems = 2, misc texts = 3,
# lectures = 4, printed texts = 5
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
            # stop the script if the csv is incorrect
            print(len(elements))
            try:
                if len(elements) == 22:
                    elements.pop(21)
                # a list of this length means there will be
                # two separate facsimiles for the publication
                elif len(elements) == 23:
                    elements.pop(22)
                    print("Version coming.")
                else:
                    raise ValueError("CSV is not correct!")
            except ValueError as e:
                print(e)
                raise
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
            # register the archive signums, old and new
            # and the archive folder, if present
            old_archive_signum = facsimile[13]
            new_archive_signum = facsimile[10]
            archive_folder = facsimile[8]
            if old_archive_signum is not None and new_archive_signum is not None and archive_folder is not None and archive_folder != "KA":
                description = old_archive_signum + ", " + new_archive_signum + ", " + archive_folder
            elif old_archive_signum is not None and new_archive_signum is not None and archive_folder == "KA":
                description = old_archive_signum + ", " + new_archive_signum
            elif old_archive_signum is not None and new_archive_signum is not None and archive_folder is None:
                description = old_archive_signum + ", " + new_archive_signum
            # this is material from another person's archive than Mechelin's,
            # but still at the National Archives
            # (if new_archive_signum ends with ".pdf", it's not from the National Archives)
            elif old_archive_signum is None and new_archive_signum is not None and not new_archive_signum.endswith(".pdf") and archive_folder is not None:
                description = new_archive_signum + ", " + archive_folder
            # this is material from another archive than the National Archives
            else:
                description = archive_folder
            external_url = facsimile[14]
            publication_id = facsimile[19]
            first_image = facsimile[11]
            last_image = facsimile[12]
            facsimile_paths_orig = facsimile[18]
            facsimile_paths_version = ""
        # this is a publication with 2 separate facsimiles
        if len(facsimile) == 22:
            title = facsimile[21]
            old_archive_signum = facsimile[13]
            new_archive_signum = facsimile[10]
            archive_folder = facsimile[8]
            if old_archive_signum is not None and new_archive_signum is not None and archive_folder is not None and archive_folder != "KA":
                description = old_archive_signum + ", " + new_archive_signum + ", " + archive_folder
            elif old_archive_signum is not None and new_archive_signum is not None and archive_folder == "KA":
                description = old_archive_signum + ", " + new_archive_signum
            elif old_archive_signum is not None and new_archive_signum is not None and archive_folder is None:
                description = old_archive_signum + ", " + new_archive_signum
            # this is material from another person's archive than Mechelin's,
            # but still at the National Archives
            # (if new_archive_signum ends with ".pdf", it's not from the National Archives)
            elif old_archive_signum is None and new_archive_signum is not None and not new_archive_signum.endswith(".pdf") and archive_folder is not None:
                description = new_archive_signum + ", " + archive_folder
            # this is material from another archive than the National Archives
            else:
                description = archive_folder
            external_url = facsimile[14]
            publication_id = facsimile[20]
            first_image = facsimile[11]
            last_image = facsimile[12]
            if last_image is None:
                last_image = first_image
            facsimile_paths_orig = facsimile[18]
            facsimile_paths_version = facsimile[19]
        print(first_image)
        first_image = int(re.sub("^0+", "", first_image))
        last_image = int(re.sub("^0+", "", last_image))
        # number_of_pages in db means number of images
        number_of_pages = last_image - first_image + 1
        if first_image == last_image:
            # include new_archive_signum if it comes from an archive
            # using a separate pdf as the facsimile for each publication, 
            # since normal image numbering isn't descriptive enough in that case
            if new_archive_signum.endswith(".pdf"):
                page_comment = new_archive_signum + ", " + str(first_image)
            else:
                page_comment = str(first_image)
        else:
            if new_archive_signum.endswith(".pdf"):
                page_comment = new_archive_signum + ", " + str(first_image) + "–" + str(last_image)
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

def copy_images_to_facs_folders(file_list, facs_coll_id):
    i = 0
    for file in file_list:
        file_number = 1 + i
        print(file + ", " + str(file_number))
        copyfile(str(file), WEB_FACSIMILE_FOLDER + str(facs_coll_id) + "/1/" + str(file_number) + ".jpg")
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

'''
sample input:
18.3.1866;Saapunut sähke;;m;Forselles, Carl af;Forselles konkurs, Tammerfors Linne- och Jern-Manufaktur Aktie-Bolag;ranska;KA;1;1441958557;0001;0001;1341774.KA;https://astia.narc.fi/astiaUi/digiview.php?imageId=10316479&aytun=1341774.KA&j=1;;;;['M:/Faksimiili/Mechelin 1/1341774.KA/jpeg/0001.jpg'];1217;18.3.1866 Carl af Forselles–LM;
'''