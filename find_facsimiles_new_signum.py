# This script finds out which images belong to which document,
# and then stores the file paths to those images.

# The starting point is a csv file with info about the publication
# and its images. The first and last image signum of each publication's
# facsimile is in the file, but we need to modify the signums a bit.
# We have image folders named after the archive signums,
# and images named after the image signums, but we don't want to
# have to go through those folders and images by hand.

# Furthermore, the archive which digitized the images has changed
# its way of creating folder signums. These publications use the
# new signum, others use the old. Both signums should be registered
# for each publication. We already made a dictionary of old and new
# signums.

# The output is a csv containing more info than before for each
# publication: the old and new folder signum, the first and last
# image signum and the file paths to the images. This csv will be
# used for populating table publication as well as for creating the
# facsimile folder and its images and connecting the folder to the
# publication.

# We can either create the list of all possible image file paths
# from the given facsimile folder path, and then save the newly created
# list as a txt file for later use, or we can use a txt file created
# earlier and read it into a list. If no images have been added to the
# facsimile folder recently, reading the file paths from file instead of
# creating the list from scratch speeds up this script a lot.

# Sample input and output (CSV) at end of file.

import re
import json
from pathlib import Path

CSV_IN = "csv/documents_2.csv"
CSV_OUT = "csv/documents_2_facsimiles.csv"
FACSIMILE_FILE_PATHS = "new_signum_facsimile_file_paths.txt"
FACSIMILE_FOLDERS = ["M:/Facsimiles/Mechelin_1", "M:/Facsimiles/Mechelin_2", "M:/Facsimiles/Mechelin_3"]

# create a list from the original csv file 
def create_list_from_csv(filename):
    with open(filename, "r", encoding="utf-8-sig") as source_file:
        list = []
        for line in source_file:
            row = line.rstrip()
            elements = row.split(";")
            list.append(elements)
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
                output_file.write(str(item) + ";")
            output_file.write("\n")
        print("List written to file", filename)

# create path object for folder from given filepath string,
# save all paths to files found in this folder or subfolders in a list
def create_file_list(folder_path):
    file_list = []
    for path in folder_path:
        path = Path(path)
        iterate_through_folders(path, file_list)
    print("List of image file paths created.")
    return file_list

# iterate through folders recursively and append filepaths to list
def iterate_through_folders(path, file_list):
    for content in path.iterdir():
        if content.is_dir():
            iterate_through_folders(content, file_list)
        else:
            file_list.append(content)

# save the list of all facsimile file paths as a file
# thus the script runs faster next time
def write_list_to_text_file(file_list, filename):
    with open(filename, "w", encoding="utf-8-sig") as output_file:
        for path in file_list:
            output_file.write(path.as_posix())
            output_file.write('\n')
        print("List of facsimile file paths written to file", filename)

# if a file containing all facsimile file paths
# has already been created:
# read that file into a list
def read_list_from_file(filename):
    with open(filename, encoding="utf-8-sig") as source_file:
        data = source_file.read()
        data_list = data.split("\n")
        source_file.close()
        file_list = []
        for path in data_list:
            path = Path(path)
            file_list.append(path)
        print("List of facsimile file paths created from file.")
        return file_list

# we need to find the folder signum as well as
# the signum/number of the first and last image
# for each publication
def find_signums(info_list, file_list, signum_dictionary):
    # look for a signum and split it into two parts:
    # the folder signum and the image signum
    # add the found signums to each list in the info_list
    for row in info_list:
        # look for folder and image signums
        whole_first_signum = row.pop(11)
        search_string = re.compile(r"(\d{10})_(\d{4})")
        match_string = re.search(search_string, whole_first_signum)
        # if no signum is found we can't find the facsimile with this script
        # empty that list
        if match_string is None:
            print("No facsimiles found for:")
            print(row)
            row.clear()
            continue
        # remove this empty slot in the list, placeholder for folder signum
        row.pop(10)
        # add the newly found signums to list
        folder_signum = match_string.group(1)
        first_image_signum = match_string.group(2)  
        row.insert(10, folder_signum)
        row.insert(11, first_image_signum)
        # look for a second signum and split it, if found
        whole_last_signum = row.pop(12)
        match_string = re.search(search_string, whole_last_signum)
        # if no second signum was found, then the facsimile is just one image
        if match_string is None:
            last_image_signum = first_image_signum
        else:
            last_image_signum = match_string.group(2)
        row.insert(12, last_image_signum)
        # check for a version signum; if there are alternative images,
        # we need to add a second facsimile for this publication
        if row[15] != "":
            version_signum = row[15]
            version_first_image_signum = row[16]
            # if no second signum is found, then the facsimile is just one image
            if row[17] != "":
                version_last_image_signum = row[17]
            else:
                version_last_image_signum = version_first_image_signum
        else:
            version_signum = ""
            version_first_image_signum = ""
            version_last_image_signum = ""
        # find file paths for all images, save file paths as list,
        # append to current list
        match_list, match_list_2 = find_image_paths(folder_signum, first_image_signum, last_image_signum, version_signum, version_first_image_signum, version_last_image_signum, file_list)
        row.extend([match_list])
        if match_list_2 != "":
            row.extend([match_list_2])            
        old_folder_signum = find_old_folder_signum(folder_signum, signum_dictionary)
        # placeholder for old folder signum
        row.pop(13)
        row.insert(13, old_folder_signum)
        print(row)
    # get rid of empty lists
    result_list = [row for row in info_list if row != []]
    return result_list

# we've got a list of all file paths to images
# we have to find the right path(s) for this publication's images
def find_image_paths(folder_signum, first_image_signum, last_image_signum, version_signum, version_first_image_signum, version_last_image_signum, file_list):
    i = 0
    match_list = []
    first_image = int(re.sub("^0+", "", first_image_signum))
    last_image = int(re.sub("^0+", "", last_image_signum))
    while i < len(file_list) - 1:
        file_path = file_list[i]
        match_str = re.search(folder_signum, str(file_path))
        image = str(file_path.stem)
        if match_str and first_image_signum == image:
            match_list.append(file_path.as_posix())
            for number in range(first_image + 1, last_image + 1):
                image_name = str(number).zfill(4) + ".jpg"
                file_path = file_path.with_name(image_name)
                match_list.append(file_path.as_posix())
            break
        i += 1
    if not match_list:
        print(folder_signum + " and " + str(first_image_signum) + " not found among file paths.")
        match_list = ""
    if version_signum != "":
        i = 0
        match_list_2 = []
        first_image = int(re.sub("^0+", "", version_first_image_signum))
        last_image = int(re.sub("^0+", "", version_last_image_signum))
        while i < len(file_list) - 1:
            file_path = file_list[i]
            match_str = re.search(version_signum, str(file_path))
            image = str(file_path.stem)
            if match_str and version_first_image_signum == image:
                match_list_2.append(file_path.as_posix())
                for number in range(first_image + 1, last_image + 1):
                    image_name = str(number).zfill(4) + ".jpg"
                    file_path = file_path.with_name(image_name)
                    match_list_2.append(file_path.as_posix())
                break
            i += 1
        if not match_list_2:
            print("Version " + folder_signum + " and " + str(first_image_signum) + " not found among file paths.")
            match_list_2 = ""
    else:
        match_list_2 = ""
    return match_list, match_list_2

# use new folder signum to find its old equivalent from dictionary
# add old signum to list
def find_old_folder_signum(folder_signum, signum_dictionary):
    for key, value in signum_dictionary.items():
        if folder_signum == value:
            old_folder_signum = key
            break
    if folder_signum not in signum_dictionary.values() or not old_folder_signum:
        print(folder_signum + " not found in signum_dictionary.")
        old_folder_signum = ""
    return old_folder_signum

def main():
    # info about publications
    info_list = create_list_from_csv(CSV_IN)
    # get a list of all facsimile file paths,
    # either from an existing txt file
    # or by creating the list from scratch
    # and saving it as a txt file for later use
    if FACSIMILE_FILE_PATHS != "":
        file_list = read_list_from_file(FACSIMILE_FILE_PATHS)
    else:
        file_list = create_file_list(FACSIMILE_FOLDERS)
        write_list_to_text_file(file_list, "new_signum_facsimile_file_paths.txt")
    # old and new folder signums from dictionary
    signum_dictionary = read_dict_from_file("dictionaries/signum_dictionary.json")
    # append folder signum, first and last image signum,
    # file paths to images, old folder signum
    result_list = find_signums(info_list, file_list, signum_dictionary)
    write_list_to_csv(result_list, CSV_OUT)

main()

'''
sample input:
1.10.1878;luento;x;;Finlands statsrätt;8 föreläsningen;;ruotsi;64 LM/KA;2;;1441481490_0147;1441481490_0148;;;;;
sample output:
1.10.1878;luento;x;;Finlands statsrätt;8 föreläsningen;;ruotsi;64 LM/KA;2;1441481490;0147;0148;1909976.KA;;;;;['M:/Faksimiili/Mechelin_11/1441481490/master/0147.jpg', 'M:/Faksimiili/Mechelin_11/1441481490/master/0148.jpg'];
'''
