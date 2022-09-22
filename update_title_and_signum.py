# This script updates publication titles and archive signums
# in tables publication_manuscript and publication_facsimile_collection.

import psycopg2

conn_db = psycopg2.connect(
    host="",
    database="",
    user="",
    port="",
    password=""
)
cursor = conn_db.cursor()

COLLECTION_ID = 1
DELETED = 0
LANGUAGE = "sv"

# fetch the correct up-to-date title and archive signum
# for each publication
# they're in tables translation_text and publication
# also fetch the publication_facsimile_collection_id
# that will be used for updating the info in 
# table publication_facsimile_collection
def fetch_publication_data():
    field_name = "name"
    fetch_query = """SELECT publication.id, archive_signum, text, publication_facsimile_collection_id FROM publication, translation_text, publication_facsimile WHERE publication_collection_id = %s AND publication.deleted = %s AND translation_text.language = %s AND publication.translation_id = translation_text.translation_id AND field_name = %s AND publication.id = publication_facsimile.publication_id"""
    values_to_insert = (COLLECTION_ID, DELETED, LANGUAGE, field_name)
    cursor.execute(fetch_query, values_to_insert)
    publications = cursor.fetchall()
    return publications

# fetch the title and archive signum that are currently in
# table publication_manuscript
# check whether they're the same as the ones fetched in
# fetch_publication_data
# if not, update the info in this table
def update_publication_manuscript(publication_id, archive_signum, title):
    fetch_query = """SELECT name, archive_signum FROM publication_manuscript WHERE publication_id = %s"""
    value_to_insert = (publication_id,)
    cursor.execute(fetch_query, value_to_insert)
    manuscript_data = cursor.fetchone()
    if manuscript_data is not None:
        (old_title, old_archive_signum) = manuscript_data
        if title != old_title:
            update_query = """UPDATE publication_manuscript SET name = %s WHERE publication_id = %s"""
            value_to_update = (title, publication_id)
            cursor.execute(update_query, value_to_update)
            print("ms " + old_title + " -> " + title)
        if archive_signum is not None and archive_signum != old_archive_signum:
            update_query = """UPDATE publication_manuscript SET archive_signum = %s WHERE publication_id = %s"""
            value_to_update = (archive_signum, publication_id)
            cursor.execute(update_query, value_to_update)

# fetch the title and archive signum that are currently in
# table publication_facsimile_collection
# check whether they're the same as the ones fetched in
# fetch_publication_data
# if not, update the info in this table
# make sure not to overwrite titles for versions
# or facsimile links, because they're never the same
# as the publication's title; leave these titles out
# of the update operation
# also don't update the archive signums of versions, since they
# may be different from the original publication's signum
def update_publication_facsimile_collection(publication_facsimile_collection_id, archive_signum, title):
    facsimile_type = 0 # facsimile links
    priority = 1 # not a version
    fetch_query = """SELECT title, description FROM publication_facsimile_collection, publication_facsimile WHERE publication_facsimile_collection.id = %s AND NOT type = %s AND priority = %s AND publication_facsimile_collection.id = publication_facsimile.publication_facsimile_collection_id"""
    values_to_insert = (publication_facsimile_collection_id, facsimile_type, priority)
    cursor.execute(fetch_query, values_to_insert)
    facsimile_data = cursor.fetchone()
    if facsimile_data is not None:
        (old_title, old_archive_signum) = facsimile_data
        if title != old_title:
            update_query = """UPDATE publication_facsimile_collection SET title = %s WHERE id = %s"""
            value_to_update = (title, publication_facsimile_collection_id)
            cursor.execute(update_query, value_to_update)
            print("facsimile " + old_title + " -> " + title)
        # this indicates that the archive signum in this table
        # has been updated more recently than the one in table
        # publication, it has been corrected in the wrong place
        # transfer this info to table publication (by hand) and
        # don't overwrite it here
        if archive_signum is not None and len(old_archive_signum) > len(archive_signum):
            print("facs_coll_id: " + str(publication_facsimile_collection_id) + ", signum: " + old_archive_signum + " should be checked up!")
            archive_signum = old_archive_signum
        if archive_signum is not None and archive_signum != old_archive_signum:
            update_query = """UPDATE publication_facsimile_collection SET description = %s WHERE id = %s"""
            value_to_update = (archive_signum, publication_facsimile_collection_id)
            cursor.execute(update_query, value_to_update)
            print(old_archive_signum + " -> " + archive_signum)

def main():
    publications = fetch_publication_data()
    for publication in publications:
        (publication_id, archive_signum, title, publication_facsimile_collection_id) = publication
        update_publication_manuscript(publication_id, archive_signum, title)
        update_publication_facsimile_collection(publication_facsimile_collection_id, archive_signum, title)
    conn_db.commit()
    print("Tables updated.")
    conn_db.close()
    cursor.close()

main()