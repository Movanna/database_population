# This script updates tables translation, translation_text,
# publication_collection and publication_group and inserts
# translations for the titles of the collections and groups.

import psycopg2
from psycopg2 import sql

conn_db = psycopg2.connect(
    host="",
    database="",
    user="",
    port="",
    password=""
)
cursor = conn_db.cursor()

# fetch the titles of the collections and groups
def get_db_info(table):
    fetch_query = """SELECT name, id FROM {}"""
    cursor.execute(sql.SQL(fetch_query).format(sql.Identifier(table)))
    db_info = cursor.fetchall()
    return db_info

# populate table translation
def create_translation():
    neutral_text = "No translation found"
    insert_query = """INSERT INTO translation(neutral_text) VALUES(%s) RETURNING id"""
    value_to_insert = (neutral_text,)
    cursor.execute(insert_query, value_to_insert)
    translation_id = cursor.fetchone()[0]
    return translation_id

# populate table translation_text with titles for collections
# and groups
# we don't have the translated titles yet, so we'll just
# insert the swe titles as they are and change them later
def create_translation_text(translation_id, title, table):
    language = "fi"
    field_name = "name"
    insert_query = """INSERT INTO translation_text(translation_id, language, text, field_name, table_name) VALUES(%s, %s, %s, %s, %s)"""
    values_to_insert = (translation_id, language, title, field_name, table)
    cursor.execute(insert_query, values_to_insert)

# update tables publication_collection and publication_group
# with translation_id for the titles of the collections/groups
# generate sql dynamically in order to merge table names to the query
# that can't be done by using %s placeholders, since Psycopg will
# try quoting the table name as a string value, generating invalid sql
def update_group_or_collection(table, translation_id, id):
    update_query = """UPDATE {} SET translation_id = %s WHERE id = %s"""
    values_to_insert = (translation_id, id)
    cursor.execute(sql.SQL(update_query).format(sql.Identifier(table)), values_to_insert)

def main():
    # these are the tables we want to update
    tables = ["publication_collection", "publication_group"]
    for table in tables:
        db_info = get_db_info(table)
        # whether it's a collection or a group,
        # we need the swe title and the id
        for group_or_collection in db_info:
            (title, id) = group_or_collection
            translation_id = create_translation()
            # just insert the swe title since translated titles
            # are not yet available
            create_translation_text(translation_id, title, table)
            update_group_or_collection(table, translation_id, id)
    print("Tables updated.")    
    conn_db.commit()
    conn_db.close()
    cursor.close()

main()