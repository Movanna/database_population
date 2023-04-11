# This script is used for fixing flawed facsimiles that have
# already been created and added to the database and the file
# storage. Sometimes you find out afterwards that there are images
# missing, or that the images are in the wrong order.
# If you have the id of the facsimile and the file paths to the
# correct images, in the right order, this script will create
# a new facsimile folder and fill it with the new images, which are
# renamed and put into a subdirectory as required. Then the
# old folder can be replaced in the storage. This is not meaningful
# to do by hand, since all images have to be named 1, 2, 3 etc.,
# not allowing for adding e.g. 167b in between 167 and 168.

# The starting point is a csv containing the facsimile_collection_id
# for which a new facsimile should be created, and the file paths
# to the new images.

import re
import os
from shutil import copyfile

CSV_IN = "csv/fix_facsimiles.csv"
WEB_FACSIMILE_FOLDER = "M:/webbfaksimil/facsimile_collections/"

# create a list from the original csv file
# replace empty values with None
def create_list_from_csv(filename):
    with open(filename, "r", encoding="utf-8-sig") as source_file:
        list = []
        for line in source_file:
            row = line.rstrip()
            elements = row.split(";")
            list.append(elements)
        return list

def create_publication_facsimile_collection(facsimiles_to_be_created):
    for facsimile in facsimiles_to_be_created:
        facs_coll_id = facsimile[0]
        facsimile_paths = facsimile[1]
        # file paths are a list
        facsimile_paths = re.sub(r"\['|'\]", "", facsimile_paths)
        file_list = facsimile_paths.split("', '")
        create_facsimile_folders(facs_coll_id)
        copy_images_to_facs_folders(file_list, facs_coll_id)

def create_facsimile_folders(facs_coll_id):
    os.makedirs(os.path.dirname(WEB_FACSIMILE_FOLDER + str(facs_coll_id) + "/1/"), exist_ok=True)

def copy_images_to_facs_folders(file_list, facs_coll_id):
    i = 0
    for file in file_list:
        file_number = 1 + i
        print(file + ", " + str(file_number))
        copyfile(str(file), WEB_FACSIMILE_FOLDER + str(facs_coll_id) + "/1/" + str(file_number) + ".jpg")
        i += 1

def main():
    facsimiles_to_be_created = create_list_from_csv(CSV_IN)
    create_publication_facsimile_collection(facsimiles_to_be_created)
    print("New facsimiles created.")

main()