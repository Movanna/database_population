# This script updates table publication with more
# extensive archive signums.

import psycopg2

conn_db = psycopg2.connect(
    host="",
    database="",
    user="",
    port="",
    password=""
)
cursor = conn_db.cursor()

CSV_IN = "csv/mapp_65_faksimil_id.csv"

# create a list from the original csv file
# replace empty values with None
def create_list_from_csv(filename):
    with open(filename, "r", encoding="utf-8-sig") as source_file:
        list = []
        for line in source_file:
            row = line.rstrip()
            elements = row.split(";")
            for i in range(0,len(elements)):
                if elements[i] == "":
                    elements[i] = None
            list.append(elements)
        return list

def update_publication_with_folder_signum(publications):
    fetch_query = """SELECT archive_signum FROM publication WHERE id = %s"""
    update_query = """UPDATE publication SET archive_signum = %s WHERE id = %s"""
    for publication in publications:
        print(len(publication))
        if len(publication) == 22:
            publication_id = publication[19]
        elif len(publication) == 23:
            publication_id = publication[20]
        else:
            # or it might be publication[5], or [7] ... depending on csv
            publication_id = publication[13]
        folder_signum = publication[8]
        value_to_insert = (publication_id,)
        cursor.execute(fetch_query, value_to_insert)
        old_archive_signum = cursor.fetchone()[0]
        if old_archive_signum is not None and folder_signum is not None:
            new_archive_signum = old_archive_signum + ", " + folder_signum
            value_to_update = (new_archive_signum, publication_id)
            cursor.execute(update_query, value_to_update)
            print(new_archive_signum)
        else:
            print("Publication_id " + str(publication_id) + " is lacking signums!")
    print("Table publication updated.")
    conn_db.commit()

def main():
    publications = create_list_from_csv(CSV_IN)
    update_publication_with_folder_signum(publications)
    conn_db.close()
    cursor.close()

main()