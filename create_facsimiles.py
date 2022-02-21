# This script is used for fixing flawed facsimiles that have
# already been created and added to the database and the file
# storage. Sometimes you find out afterwards that there are images
# missing, or that the images are in the wrong order.
# If you have the id of the facsimile and the file paths to the
# correct images, in the right order, this script will create
# a new facsimile folder and fill it with the new images, which are
# renamed, resized and put into subdirectories as required. Then the
# old folder can be replaced in the storage. This is not meaningful
# to do by hand, since each facsimile consists of 4 subfolders holding
# different image sizes, and all images have to be named 1, 2, 3 etc.,
# not allowing for adding e.g. 167b in between 167 and 168.
# 
# The starting point is a csv containing the facsimile_collection_id
# for which a new facsimile should be created, and the file paths
# to the new images.
#
# Functions create_facsimile_folders and copy_images_to_facs_folders
# borrowed from Niklas Liljestrand (niklil) (who created them for the
# SLS digital publishing platform).

import re
import os
from shutil import copyfile
from PIL import Image

CSV_IN = "csv/fix_facsimiles.csv"

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
    os.makedirs(os.path.dirname("facsimile_collections/" + str(facs_coll_id) + "/1/"), exist_ok=True)
    os.makedirs(os.path.dirname("facsimile_collections/" + str(facs_coll_id) + "/2/"), exist_ok=True)
    os.makedirs(os.path.dirname("facsimile_collections/" + str(facs_coll_id) + "/3/"), exist_ok=True)
    os.makedirs(os.path.dirname("facsimile_collections/" + str(facs_coll_id) + "/4/"), exist_ok=True)

def copy_images_to_facs_folders(file_list, facs_coll_id):
    i = 0
    for file in file_list:
        file_number = 1 + i
        print(file + ", " + str(file_number))
        copyfile(str(file), "facsimile_collections/" + str(facs_coll_id) + "/1/" + str(file_number) + ".jpg")
        image = Image.open("facsimile_collections/" + str(facs_coll_id) + "/1/" + str(file_number) + ".jpg")
        resized_im = image.resize((round(image.size[0]*0.5), round(image.size[1]*0.5)))
        resized_im.save("facsimile_collections/" + str(facs_coll_id) + "/2/" + str(file_number) + ".jpg", quality=90, optimize=True)
        resized_im = image.resize((round(image.size[0]*0.3), round(image.size[1]*0.3)))
        resized_im.save("facsimile_collections/" + str(facs_coll_id) + "/3/" + str(file_number) + ".jpg", quality=90, optimize=True)
        resized_im = image.resize((round(image.size[0]*0.1), round(image.size[1]*0.1)))
        resized_im.save("facsimile_collections/" + str(facs_coll_id) + "/4/" + str(file_number) + ".jpg", quality=90, optimize=True)
        i += 1

def main():
    facsimiles_to_be_created = create_list_from_csv(CSV_IN)
    create_publication_facsimile_collection(facsimiles_to_be_created)
    print("New facsimiles created.")

main()