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

COLLECTION_ID = 2
UNKNOWN_TIME_PERIOD_ID = 40

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
                elif COLLECTION_ID == 2:
                    if date >= datetime.date(1873, 1, 1) and date < datetime.date(1874, 1, 1):
                        group_id = 6
                    elif date >= datetime.date(1874, 1, 1) and date < datetime.date(1877, 1, 1):
                        group_id = 13
                    elif date >= datetime.date(1877, 1, 1) and date < datetime.date(1880, 1, 1):
                        group_id = 21
                    elif date >= datetime.date(1880, 1, 1) and date < datetime.date(1882, 1, 1):
                        group_id = 30
                # if the publication's date doesn't match the time periods
                # above, either date or collection_id is wrong
                else:
                    group_id = UNKNOWN_TIME_PERIOD_ID
                    print("Publication " + str(id) + " is in the wrong collection according to its date!")
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