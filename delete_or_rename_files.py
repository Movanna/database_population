# This script makes a list of all file paths in a given
# folder and its subfolders and then either deletes files
# depending on what publication id the file name contains,
# or renames files and folders if their names contain
# a certain component.

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
# This script simply deletes the unwanted files for you and you're
# good to go again.

# Alternatively, you create files and folders and then later on discover 
# that they should have been named differently, e.g. the name of the
# sender of a letter was actually something else than you first thought.
# This sender may have hundreds of folders and files and we need to change
# their names. Just define what component in the file path you need to
# change and then have everything renamed.

from pathlib import Path
import re

FOLDER = "../documents/Part_2/Letters/Received"
DELETE = False
RENAME = True
OLD_NAME_COMPONENT = "Harald"
NEW_NAME_COMPONENT = "Herman"

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

# rename files and folders if their names contain
# a certain component
def rename_file_and_folders(file_list):
    for file in file_list:
        # get all the individual components of the path
        path_parts = list(file.parts)
        # no need to check these first parts of the path
        new_path = Path(*path_parts[:7])
        for part in path_parts[7:]:
            old_path = new_path / part
            if OLD_NAME_COMPONENT in part:
                new_path = new_path / part.replace(OLD_NAME_COMPONENT, NEW_NAME_COMPONENT)
                print(old_path)
                print(new_path)
                # check if this path still exists
                # the folder may already have been renamed
                # by an earlier iteration, since these files
                # share the same folders
                if old_path.exists():
                    old_path.rename(new_path)
            # in this case, there's nothing to rename
            # just keep going towards the end of the path
            else:
                new_path = new_path / part

def main():
    # get file paths for given folder
    file_list = create_file_list(FOLDER)
    # delete unwanted files
    if DELETE is True:
        for file in file_list:
            delete_file_depending_on_filename(file)
        print("Files deleted.")
    # rename files and folders
    if RENAME is True:
        rename_file_and_folders(file_list)
        print("Files and folders renamed.")

main()