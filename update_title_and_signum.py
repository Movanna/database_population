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

def fetch_publication_data():
    field_name = "name"
    fetch_query = """SELECT publication.id, archive_signum, text, publication_facsimile_collection_id FROM publication, translation_text, publication_facsimile WHERE publication_collection_id = %s AND publication.deleted = %s AND translation_text.language = %s AND publication.translation_id = translation_text.translation_id AND field_name = %s AND publication.id = publication_facsimile.publication_id"""
    values_to_insert = (COLLECTION_ID, DELETED, LANGUAGE, field_name)
    cursor.execute(fetch_query, values_to_insert)
    publications = cursor.fetchall()
    return publications

def update_publication_manuscript(publication_id, archive_signum, title):
    fetch_query = """SELECT name, archive_signum FROM publication_manuscript WHERE id = %s"""
    value_to_insert = (publication_id,)
    cursor.execute(fetch_query, value_to_insert)
    manuscript_data = cursor.fetchone()
    if manuscript_data is not None:
        (old_title, old_archive_signum) = manuscript_data
        if title != old_title:
            update_query = """UPDATE publication_manuscript SET name = %s WHERE publication_id = %s"""
            value_to_update = (title, publication_id)
            cursor.execute(update_query, value_to_update)
        if archive_signum is not None and archive_signum != old_archive_signum:
            update_query = """UPDATE publication_manuscript SET archive_signum = %s WHERE publication_id = %s"""
            value_to_update = (archive_signum, publication_id)
            cursor.execute(update_query, value_to_update)

def update_publication_facsimile_collection(publication_facsimile_collection_id, archive_signum, title):
    facsimile_type = 0
    fetch_query = """SELECT DISTINCT title, description, priority FROM publication_facsimile_collection, publication_facsimile WHERE publication_facsimile_collection.id = %s AND NOT type = %s"""
    values_to_insert = (publication_facsimile_collection_id, facsimile_type)
    cursor.execute(fetch_query, values_to_insert)
    facsimile_data = cursor.fetchone()
    if facsimile_data is not None:
        (old_title, old_archive_signum, priority) = facsimile_data
        if "Version /" not in old_title and "<cite>" not in old_title and priority == 1 and title != old_title:
            update_query = """UPDATE publication_facsimile_collection SET title = %s WHERE id = %s"""
            value_to_update = (title, publication_facsimile_collection_id)
            cursor.execute(update_query, value_to_update)
            print(old_title + " -> " + title)
        if archive_signum is not None and len(old_archive_signum) > len(archive_signum):
            print("facs_coll_id: " + str(publication_facsimile_collection_id) + ", signum: " + old_archive_signum)
            archive_signum = old_archive_signum
        if archive_signum is not None and archive_signum != old_archive_signum and priority == 1:
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