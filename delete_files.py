# This script makes a list of all file paths in a given
# folder and its subfolders and then deletes files
# depending on what publication id the file name contains.

# When running any of the scripts that populate table publication,
# the corresponding XML files are created simultaneously.
# But if you first test the script on your test database,
# and then forget to delete the newly created files as you
# run the script again on the production db, you end up with a
# double set of files: half of them have id:s from the test db,
# and half of them have the id:s from the production db
# that they should actually have. The names of all the different
# folders and subfolders don't contain id:s, though, and thus
# they don't change between the runs, so you can't
# delete the unwanted files without opening every subfolder.

# The db data is fine so it would be a pity to start deleting it
# or using a db backup in order to run the populating script again.
# Hence this script which simply deletes the unwanted files for you.
# Then you're good to go again.

from pathlib import Path
import re

FOLDER = "documents/Delutgava_2/Brev/Mottaget"

# create path object for folder from given filepath string,
# save all paths to files found in this folder or subfolders in a list
def create_file_list(source_folder):
    path = Path(source_folder)
    file_list = []
    iterate_through_folders(path, file_list)
    return file_list

# iterate through folders recursively and append filepaths to list
def iterate_through_folders(path, filelist):
    for content in path.iterdir():
        if content.is_dir():
            iterate_through_folders(content, filelist)
        else:
            filelist.append(content)

# publication_id is present in the file name
# delete all files where publication_id refers
# to the test database
def delete_file_depending_on_filename(file):
    file_name = file.stem
    search_string = re.compile(r"_(\d+)$")
    match = re.search(search_string, file_name)
    publication_id = match.group(1)
    publication_id = int(publication_id)
    if publication_id < 3079:
        print(file_name)
        file.unlink()

def main():
    # get file paths for given folder
    file_list = create_file_list(FOLDER)
    # delete unwanted files
    for file in file_list:
        delete_file_depending_on_filename(file)
    print("Files deleted.")

main()