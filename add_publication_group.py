# This script updates table publication.
# It finds out the right publication_group for
# each publication according to its date.

import psycopg2
import re
import datetime

conn_db = psycopg2.connect(
    host="",
    database="",
    user="",
    port="",
    password=""
)
cursor = conn_db.cursor()

COLLECTION_ID = 5
UNKNOWN_TIME_PERIOD_ID = 129

# get the relevant info for all publications in a collection
def get_publication_info():
    fetch_query = """SELECT id, publication_group_id, original_publication_date FROM publication WHERE publication_collection_id = %s"""
    cursor.execute(fetch_query, (COLLECTION_ID,))
    publications = cursor.fetchall()
    return publications

# use original_publication_date to add the right publication_group_id
def find_out_group(publications):
    for tuple in publications:
        group_id = tuple[1]
        if group_id is None:
            id = tuple[0]
            original_publication_date = tuple[2]
            print(original_publication_date)
            search_string = re.compile(r"^(.{4})-(.{2})-(.{2})")
            match_string = re.search(search_string, original_publication_date)
            if match_string:
                date = match_string.group(0)
                # if date's unknown, group will be "unknown time period"
                if date == "XXXX-XX-XX":
                    group_id = UNKNOWN_TIME_PERIOD_ID
                    add_publication_group_id(id, group_id)
                    continue
                # if we're not sure about the year, group will be
                # "unknown time period"
                year = match_string.group(1)
                if "X" in year:
                    group_id = UNKNOWN_TIME_PERIOD_ID
                    add_publication_group_id(id, group_id)
                    continue
                else:
                    year = int(year)
                month = match_string.group(2)
                if "X" in month:
                    month = 12
                else:
                    month = int(month)
                day = match_string.group(3)
                if "X" in day:
                    day = 28
                else:
                    day = int(day)
                date = datetime.date(year, month, day)
                # group depends on date
                if COLLECTION_ID == 1:
                    if date >= datetime.date(1839, 11, 24) and date < datetime.date(1860, 7, 1):
                        group_id = 1
                    elif date >= datetime.date(1860, 7, 1) and date < datetime.date(1865, 1, 1):
                        group_id = 2
                    elif date >= datetime.date(1865, 1, 1) and date < datetime.date(1867, 1, 1):
                        group_id = 3
                    elif date >= datetime.date(1867, 1, 1) and date < datetime.date(1873, 1, 1):
                        group_id = 4
                    else:
                        print("Publication " + str(id) + " doesn't match the groups in collection " + str(COLLECTION_ID))
                elif COLLECTION_ID == 2:
                    if date >= datetime.date(1873, 1, 1) and date < datetime.date(1874, 1, 1):
                        group_id = 6
                    elif date >= datetime.date(1874, 1, 1) and date < datetime.date(1877, 1, 1):
                        group_id = 13
                    elif date >= datetime.date(1877, 1, 1) and date < datetime.date(1880, 1, 1):
                        group_id = 21
                    elif date >= datetime.date(1880, 1, 1) and date < datetime.date(1882, 1, 1):
                        group_id = 30
                    else:
                        print("Publication " + str(id) + " doesn't match the groups in collection " + str(COLLECTION_ID))
                elif COLLECTION_ID == 3:
                    if date >= datetime.date(1882, 1, 1) and date < datetime.date(1885, 1, 1):
                        group_id = 51
                    elif date >= datetime.date(1885, 1, 1) and date < datetime.date(1887, 1, 1):
                        group_id = 63
                    elif date >= datetime.date(1887, 1, 1) and date < datetime.date(1889, 1, 1):
                        group_id = 76
                    elif date >= datetime.date(1889, 1, 1) and date < datetime.date(1890, 7, 1):
                        group_id = 90
                    else:
                        print("Publication " + str(id) + " doesn't match the groups in collection " + str(COLLECTION_ID))
                elif COLLECTION_ID == 4:
                    if date >= datetime.date(1890, 7, 1) and date < datetime.date(1893, 1, 1):
                        group_id = 121
                    elif date >= datetime.date(1893, 1, 1) and date < datetime.date(1896, 1, 1):
                        group_id = 122
                    elif date >= datetime.date(1896, 1, 1) and date < datetime.date(1898, 8, 1):
                        group_id = 123
                    else:
                        print("Publication " + str(id) + " doesn't match the groups in collection " + str(COLLECTION_ID))
                elif COLLECTION_ID == 5:
                    if date >= datetime.date(1898, 8, 1) and date < datetime.date(1899, 9, 1):
                        group_id = 125
                    elif date >= datetime.date(1899, 9, 1) and date < datetime.date(1900, 11, 1):
                        group_id = 126
                    elif date >= datetime.date(1900, 11, 1) and date < datetime.date(1902, 4, 1):
                        group_id = 127
                    elif date >= datetime.date(1902, 4, 1) and date < datetime.date(1903, 4, 1):
                        group_id = 128
                    else:
                        group_id = 129
                        print("Publication " + str(id) + " doesn't match the groups in collection " + str(COLLECTION_ID))
                elif COLLECTION_ID == 6:
                    if date >= datetime.date(1903, 4, 1) and date < datetime.date(1904, 2, 1):
                        group_id = 130
                    elif date >= datetime.date(1904, 2, 1) and date < datetime.date(1904, 11, 1):
                        group_id = 131
                    elif date >= datetime.date(1904, 11, 1) and date < datetime.date(1905, 8, 1):
                        group_id = 132
                    elif date >= datetime.date(1905, 8, 1) and date < datetime.date(1905, 12, 1):
                        group_id = 133
                    else:
                        group_id = 134
                        print("Publication " + str(id) + " doesn't match the groups in collection " + str(COLLECTION_ID))
                elif COLLECTION_ID == 7:
                    if date >= datetime.date(1905, 12, 1) and date < datetime.date(1906, 8, 1):
                        group_id = 135
                    elif date >= datetime.date(1906, 8, 1) and date < datetime.date(1907, 9, 1):
                        group_id = 136
                    elif date >= datetime.date(1907, 9, 1) and date < datetime.date(1908, 7, 1):
                        group_id = 137
                    else:
                        group_id = 138
                        print("Publication " + str(id) + " doesn't match the groups in collection " + str(COLLECTION_ID))
                elif COLLECTION_ID == 8:
                    if date >= datetime.date(1908, 7, 1) and date < datetime.date(1909, 6, 1):
                        group_id = 139
                    elif date >= datetime.date(1909, 6, 1) and date < datetime.date(1910, 3, 1):
                        group_id = 140
                    elif date >= datetime.date(1910, 3, 1) and date < datetime.date(1910, 7, 1):
                        group_id = 141
                    else:
                        group_id = 142
                        print("Publication " + str(id) + " doesn't match the groups in collection " + str(COLLECTION_ID))
                elif COLLECTION_ID == 9:
                    if date >= datetime.date(1910, 7, 1) and date < datetime.date(1912, 1, 1):
                        group_id = 143
                    elif date >= datetime.date(1912, 1, 1) and date < datetime.date(1913, 1, 1):
                        group_id = 144
                    elif date >= datetime.date(1913, 1, 1) and date < datetime.date(1915, 1, 1):
                        group_id = 145
                    else:
                        group_id = 146
                        print("Publication " + str(id) + " doesn't match the groups in collection " + str(COLLECTION_ID))
                else:
                    group_id = UNKNOWN_TIME_PERIOD_ID
                    print("Publication " + str(id) + " has no collection_id!")
            # if no date in the right format was found:
            # this has to be fixed
            else:
                group_id = UNKNOWN_TIME_PERIOD_ID
                print("No date in database for publication " + str(id) + "!")
            add_publication_group_id(id, group_id)
    print("Ungrouped publications in collection " + str(COLLECTION_ID) + " updated with publication_group_id.")
    conn_db.commit()

# update table publication with publication_group_id
def add_publication_group_id(id, group_id):
    update_query = """UPDATE publication SET publication_group_id = %s WHERE id = %s"""
    values_to_insert = (group_id, id)
    cursor.execute(update_query, values_to_insert)

def main():
    publications = get_publication_info()
    find_out_group(publications)
    conn_db.close()
    cursor.close()

main()