# This script finds out which images belong to which document,
# and then saves the file paths to those images.

# The starting point is a csv file with info about the publication
# and its images. The images are not from the National Archives,
# and they were delivered as TIFF and then converted to JPEG,
# which means that both the csv and this script differ a bit
# from the usual case.

# The main folder, the image folder and the number of the first image
# of each publication's facsimile is in the file, but we need to find 
# the file path(s) and the last image number.

# The output is a csv containing more info than before for each
# publication. This csv will be used for populating table publication 
# as well as for creating the facsimile folder and its images and 
# connecting the folder to the publication.

# We can either create the list of all possible image file paths
# from the given facsimile folder path, and then save the newly created
# list as a txt file for later use, or we can use a txt file created
# earlier and read it into a list. If no images have been added to the
# facsimile folder recently, reading the file paths from file instead of
# creating the list from scratch speeds up this script a lot.

# Sample input and output (CSV) at end of file.

import json
from pathlib import Path

CSV_IN = "csv/brev/Ehrstrom.csv"
CSV_OUT = "csv/brev/Ehrstrom_faksimil.csv"
FACSIMILE_FILE_PATHS = "HKA_facsimile_file_paths.txt"
FACSIMILE_FOLDERS = ["M:/Faksimiili/Ehrstrom_HKA/jpg/Mechelin_Leo_1897_1900", "M:/Faksimiili/Ehrstrom_HKA/jpg/Mechelin_Leo_1901", "M:/Faksimiili/Ehrstrom_HKA/jpg/Mechelin_Leo_1902_1904", "M:/Faksimiili/Ehrstrom_HKA/jpg/Mechelin_Leo_1905_1913"]

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
        print(path)
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

# if a file containing all facsimile file paths has already been created:
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

# we need to find the image file paths for each publication
# and also record the number of the last image, as image numbers
# are part of the metadata for each publication
def append_image_paths(info_list, file_list):
    result_list = []
    for row in info_list:
        # folder_signum is the main folder and the image folder
        # combined as e.g. "Mechelin_Leo_1897_1900/003"
        # after finding the images this value is no longer needed
        # as such, but as the image folder's number represents
        # the name of the pdf the images were extracted from, 
        # we need to record that for later use in the metadata
        folder_signum = row[10]
        folder_signum_split = folder_signum.split("/")
        pdf_number = folder_signum_split[1] + ".pdf"
        row[10] = pdf_number
        # find file paths for all images belonging to this publication
        # also find out the number of the last image
        # save file paths as list and append to current list
        match_list, last_image_number = find_image_paths(folder_signum, file_list)
        row.extend([match_list])
        row[12] = last_image_number
        result_list.append(row)
        print(row)
    return result_list

# we've got a list of all file paths to images
# we have to find the right path(s) for this publication's images
def find_image_paths(folder_signum, file_list):
    i = 0
    match_list = []
    while i < len(file_list) - 1:
        file_path = file_list[i]
        next_file_path = file_list[i + 1]
        relative_path_pattern = folder_signum + "/*.jpg"
        if file_path.match(relative_path_pattern):
            match_list.append(file_path.as_posix())
            if not next_file_path.match(relative_path_pattern):
                # if next row's main folder and image folder
                # don't match the current ones,
                # then the current file path contains
                # the last image for this publication
                last_image_number = str(file_path.stem)
                break
        i += 1
    if not match_list:
        print(folder_signum + " not found among file paths.")
        match_list = ""
        last_image_number = ""
    return match_list, last_image_number

def main():
    # info about publications
    info_list = create_list_from_csv(CSV_IN)
    # get a list of all facsimile file paths, either from an existing txt file
    # or by creating the list from scratch and saving it as a txt file for later use
    if FACSIMILE_FILE_PATHS != "":
        file_list = read_list_from_file(FACSIMILE_FILE_PATHS)
    else:
        file_list = create_file_list(FACSIMILE_FOLDERS)
        write_list_to_text_file(file_list, "HKA_facsimile_file_paths.txt")
    # update folder signum, insert last image number, append file paths to images
    result_list = append_image_paths(info_list, file_list)
    write_list_to_csv(result_list, CSV_OUT)

main()

'''
sample input:
18.6.1897;lähetetty kirje;x;;Ehrström, Erik;utrikespropaganda, skrivelse, Neovius;;ruotsi;Eb:9 Erik Ehrströmin arkisto HKA;3;Mechelin_Leo_1897_1900/001;001;;;https://yksa.disec.fi/Yksa4/download/167532763467600/file/07f22138-c442-400b-a92e-506f7586beb7;;;
sample output:
18.6.1897;lähetetty kirje;x;;Ehrström, Erik;utrikespropaganda, skrivelse, Neovius;;ruotsi;Eb:9 Erik Ehrströmin arkisto HKA;3;001.pdf;001;002;;https://yksa.disec.fi/Yksa4/download/167532763467600/file/07f22138-c442-400b-a92e-506f7586beb7;;;;['M:/Faksimiili/Ehrstrom_HKA/jpg/Mechelin_Leo_1897_1900/001/001.jpg', 'M:/Faksimiili/Ehrstrom_HKA/jpg/Mechelin_Leo_1897_1900/001/002.jpg'];
'''