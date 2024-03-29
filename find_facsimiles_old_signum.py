# This script finds out which images belong to which document,
# and then saves the file paths to those images.

# The starting point is a csv file with info about documents,
# in this case received letters.
# These letters will become publications in our edition.
# An url has been recorded for each letter.
# The url contains an archive signum and an image signum/number
# for the document's first image.
# We need to find out the (probable) last signum too, so that
# we can find all images belonging to a publication, not just the
# first one. We also need to store the file paths for these images.
# We have image folders named after the archive signums,
# and images named after the image signums, but we don't want to
# have to go through those folders and images by hand.

# If we can't calculate the last image signum, we'll use the list of
# all image file paths to look for the right images.

# Furthermore, the archive which digitized the images has later changed
# its way of creating folder signums. These publications use the
# old signum, others use the new. Therefore a dictionary containing old
# and new signums is needed; luckily the archive provided a list.
# Both signums should be registered for each publication.

# The output is a csv containing more info than before for each
# publication: the old and new folder signum, the first and last image
# signum and the file paths to the images. This csv will be used for
# populating table publication as well as for creating the facsimile
# folder and its images and connecting the folder to the publication.

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

CSV_IN = "csv/documents_1.csv"
CSV_OUT = "csv/documents_1_facsimiles.csv"
FACSIMILE_FILE_PATHS = ""
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

# we need to find the folder signum as well as
# the signum/number of the first image for each publication
def find_first_signum(info_list):
    # look for a signum (part of an url) and split it into two parts:
    # the folder signum and the publication's first image
    # construct the image signum by padding the image number with zeros
    # add the found signums to each list in the info_list
    for row in info_list:
        url = row[14]
        # the number of pages may or may not have been recorded
        # it can also have been recorded as e.g. "2+4",
        # meaning 2 pages + a separate version with 4 pages
        # get the first number
        number_of_pages = row[9]
        match_string = re.match(r"\d+", number_of_pages)
        if match_string is None or number_of_pages == "":
            row[9] = 0
        else:
            number_of_pages = int(match_string.group())
            row[9] = number_of_pages
        # look for signums in the url
        search_string = re.compile(r"aytun=(\d{7}\.KA)&j=(\d+)")
        match_string = re.search(search_string, url)
        # if no signum is found we can't find the facsimile with this script
        # empty that list
        if match_string is None:
            print("No facsimiles found for:")
            print(row)
            row.clear()
        else:
            folder_signum = match_string.group(1)
            first_image = match_string.group(2)
            first_image_signum = first_image.zfill(4)
            row[13] = folder_signum
            row[11] = first_image_signum
            row.append(first_image)
    # get rid of empty lists
    info_list = [row for row in info_list if row != []]
    # sort the info_list by two criteria: first by row[13], i.e. folder_signum
    # then by row[11], i.e. first_image_signum
    # the list needs to be sorted like this in order for us to easily
    # find out the number of the last image
    info_list.sort(key = lambda row: (row[13], row[11]))
    print("Info list created.")
    return info_list

# create path object for folder from given filepath string,
# save all paths to files found in this folder or subfolders in a list
def create_file_list(folder_path):
    file_list = []
    for path in folder_path:
        path = Path(path)
        iterate_through_folders(path, file_list)
    print("List of facsimile file paths created.")
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

# we need to find out the probable signum of the last image for each publication
def find_last_signum(extended_info_list, file_list):
    result_list = []
    i = 0
    while i < (len(extended_info_list) - 1):
        row = extended_info_list[i]
        number_of_pages = int(row[9])
        folder_signum = row[13]
        first_image = int(row[18])
        first_image_signum = row[11]
        # get the folder_signum of the following row in the list
        next_folder = extended_info_list[i + 1][13]
        # if this folder_signum is the same as on our row: store its first_image value
        if next_folder == folder_signum:
            next_publication_starts = int(extended_info_list[i + 1][18])
            # now we can find out the probable signum of the last image of
            # our publication
            # two different publications are sometimes in the same image,
            # as an image may contain one, two or even three pages, and
            # sometimes the last page of one publication and the first page
            # of another 
            # this means that in some cases the if-statement's answer will be
            # off by one, but it's our best guess
            # there's simply no way of knowing if the first image of the next
            # publication also contains the last page of the previous
            # publication or not without looking at the images
            # a number of pages value has sometimes been recorded, but since
            # it doesn't correspond with the number of images, it's not of
            # any real use, apart from in the case where number of pages == 2:
            # since these manuscripts are usually written recto/verso and not
            # every page on a new, separate piece of paper, pages 1 & 2 
            # thus aren't usually in the same image
            # (but pages 2 & 3 may be in the same image, depending on how the sheet
            # is folded)
            if next_publication_starts == first_image + 1 and number_of_pages == 2:
                last_image = next_publication_starts
            elif next_publication_starts > first_image:
                last_image = next_publication_starts - 1
            else:
                last_image = next_publication_starts
            last_image_signum = str(last_image).zfill(4)
        else:
            last_image = None
            last_image_signum = ""
        # find file paths for all images, save file paths as list, append to
        # current list
        last_image_signum, match_list = find_image_paths(folder_signum, first_image, first_image_signum, last_image, last_image_signum, file_list)
        # first_image value is no longer needed
        row.pop(18)
        row[12] = last_image_signum
        row.extend([match_list])
        result_list.append(row)
        i += 1
    # handle last row in the list
    # we can't look for next folder
    if i == (len(extended_info_list) - 1):
        row = extended_info_list[i]
        folder_signum = row[13]
        first_image = int(row[18])
        first_image_signum = row[11]
        last_image = None
        last_image_signum = ""
        # find file paths for all images, save file paths as list, append to current list
        last_image_signum, match_list = find_image_paths(folder_signum, first_image, first_image_signum, last_image, last_image_signum, file_list)
        # first_image value is no longer needed
        row.pop(18)
        row[12] = last_image_signum
        row.extend([match_list])
        result_list.append(row)
    return result_list

# we've got a list of all file paths to images
# we have to find the right path(s) for this publication's images
# we always know the number of the first image
# if we don't know the last image signum yet, we'll find it
def find_image_paths(folder_signum, first_image, first_image_signum, last_image, last_image_signum, file_list):
    # if we know the last image's number, we can look for the file path for
    # the first image, and then construct the other file paths
    if last_image:
        x = 0
        match_list = []
        while x < len(file_list) - 1:
            file_path = file_list[x]
            match_str = re.search(folder_signum, str(file_path))
            image = str(file_path.stem)
            if match_str and first_image_signum == image:
                match_list.append(file_path.as_posix())
                for number in range(first_image + 1, last_image + 1):
                    image_name = str(number).zfill(4) + ".jpg"
                    file_path = file_path.with_name(image_name)
                    match_list.append(file_path.as_posix())
                break
            x += 1
        if not match_list:
            print(folder_signum + " and " + str(first_image_signum) + " not found among file paths.")
            match_list = ""
    # if we don't know the last image, that means that from the number of
    # the first image and counting upwards, the folder only contains images
    # for our publication
    # as long as we can find file paths with the same folder signum,
    # we know these are paths to this publication's images
    # therefore this clause will also find out the last image signum
    else:
        x = 0
        match_list = []
        more_than_one_image = False
        while x < len(file_list) - 1:
            file_path = file_list[x]
            match_str = re.search(folder_signum, str(file_path))
            image = str(file_path.stem)
            if match_str and (first_image_signum == image or more_than_one_image):
                match_list.append(file_path.as_posix())
                next_path = file_list[x + 1]
                next_match_str = re.search(folder_signum, str(next_path))
                if next_match_str:
                    more_than_one_image = True
                    x += 1
                    continue
                else:
                    last_image_signum = image
                    break
            x += 1
        if not match_list:
            print(folder_signum + " and " + str(first_image_signum) + " not found among file paths.")
            match_list = ""
    return last_image_signum, match_list

# use old folder signum as key to find its new equivalent from dictionary
# add new signum to list
def find_new_folder_signum(result_list, signum_dictionary):
    for row in result_list:
        old_folder_signum = row[13]
        if old_folder_signum in signum_dictionary.keys():
            new_signum = signum_dictionary[old_folder_signum]
        else:
            new_signum = ""
        row[10] = new_signum
    return result_list

def main():
    # info about publications
    info_list = create_list_from_csv(CSV_IN)
    # append folder signum, first image signum
    extended_info_list = find_first_signum(info_list)
    # get a list of all facsimile file paths,
    # either from an existing txt file
    # or by creating the list from scratch
    # and saving it as a txt file for later use
    if FACSIMILE_FILE_PATHS != "":
        file_list = read_list_from_file(FACSIMILE_FILE_PATHS)
    else:
        file_list = create_file_list(FACSIMILE_FOLDERS)
        write_list_to_text_file(file_list, "old_signum_facsimile_file_paths.txt")
    # append last image signum, file paths
    result_list = find_last_signum(extended_info_list, file_list)
    # old and new folder signums from dictionary
    signum_dictionary = read_dict_from_file("dictionaries/signum_dictionary.json")
    # append new folder signum
    final_result_list = find_new_folder_signum(result_list, signum_dictionary)
    write_list_to_csv(final_result_list, CSV_OUT)

main()

'''
sample input:
18.2.1873;saapunut kirje;;;Rönnbäck, S.;stockaffärer;;ruotsi;KA;1;;;;;https://astia.narc.fi/astiaUi/digiview.php?imageId=10317703&aytun=1392436.KA&j=3;;;
sample output:
18.2.1873;saapunut kirje;;;Rönnbäck, S.;stockaffärer;;ruotsi;KA;1;1443045825;0003;0003;1392436.KA;https://astia.narc.fi/astiaUi/digiview.php?imageId=10317703&aytun=1392436.KA&j=3;;;;['M:/Faksimiili/Mechelin 3/1392436.KA/jpeg/0003.jpg'];
'''
