# The starting point: a large Excel file containing info about documents,
# including the name of the author of each document. The names have been
# recorded differently, sometimes as "Surname, Forename(s)", and sometimes
# as "Forename(s) Surname". The same person may have been recorded several
# times in different ways. We need to get the names correctly ordered
# so that duplicates and errors can be found.
#
# E.g. when you see "Reuter, J. N.", "Reuter, Julio" and "Reuter, Julio Nathanael"
# next or close to each other in the output list, you can identify them as
# the same person. This is a lot harder in the original Excel file, since you
# won't get "J. N. Reuter" next to "Reuter, Julio".
#
# The purpose of this script is to split each name into surname and forename(s)
# and produce an ordered list. The original version(s) of each name is/are also
# preserved in the output list. Each entry will automatically be given an ID,
# and after the output list has been manually corrected, that list will be used
# for making a dictionary containing the original values and the corrsponding ID:s.
# Thus I can later continue using the project's original Excel file for extracting
# more info, while now being able to connect the info to the right person-ID.
# E.g. info from rows containing the name "Calamnius, Fanny" and info from rows
# containing "Fanny Aurora Calamnius" can be linked to the same person-ID using
# the dictionary.
#
# This is the first step in the process of populating table subject, which holds 
# info about all persons relevant to the texts in this project.

# create a list from the original csv file 
def create_list_from_csv(filename):
    with open(filename, "r", encoding="utf-8-sig") as source_file:
        persons_list = []
        for line in source_file:
            row = line.rstrip()
            elements = row.split(";")
            persons_list.append(elements)
        return persons_list

# create a csv file 
def write_list_to_csv(persons_list, filename):
    with open(filename, "w", encoding="utf-8-sig") as output_file:
        for row in persons_list:
            for item in row:
                output_file.write(item + ";")
            output_file.write("\n")

# The csv Personer_oordnade has two values: the name, as in the project's
# original Excel file, and the name again, if necessary modified by hand
# in order to be easier to process (as the name field sometimes contains
# more than just the name). I want the output file to contain the original
# name value and the new values created by the script.
# The new values are split versions of the (modified) name value, with
# surname and forenames separated and ordered. The modified values are not
# stored in the output, beause I only need the original value and
# the separated and sorted names.
def main():
    persons_list = create_list_from_csv("csv/Personer_oordnade.csv")
    for row in persons_list:
        original = row[0]
        name = row.pop(1)
        # find names written as "Surname, Forename"
        if name.find(",") != -1:
            surname_and_forename = name.split(", ", 1)
            row.extend(surname_and_forename)
            forename = row[-1]
            if forename.find(" ") != -1:
                forename = row.pop(-1)
                forename_split = forename.split(" ")
                row.extend(forename_split)
        # find names written as "Forename Surname"
        else:
            split_name = name.split(" ")
            row.extend(split_name)
            surname = row.pop()
            row.insert(1, surname)
    # sort the list of lists according to column 2 (row[1]), i.e. surname
    persons_list.sort(key = lambda row: row[1])
    print(persons_list)
    write_list_to_csv(persons_list, "csv/personer_ordnade.csv")

main()