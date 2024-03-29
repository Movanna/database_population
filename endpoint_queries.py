# This script handles the database queries for the API endpoints.
# Please see api_endpoints.py in this repo. 

import os
import re
from sqlalchemy.sql import text
from sqlalchemy import create_engine
from sqlalchemy.engine import url

DATABASE = {
    "drivername": "",
    "host": os.getenv(""),
    "port": os.getenv(""),
    "username": os.getenv(""),
    "password": os.getenv(""),
    "database": os.getenv("")
}
db_engine = create_engine(url.URL.create(**DATABASE))
project = os.getenv("")

# find out the collection for a specific publication
def find_out_collection(publication_id):
    connection = db_engine.connect()
    select ="SELECT publication_collection_id FROM publication WHERE id = :p_id AND deleted = 0;"
    statement = text(select).bindparams(p_id=publication_id)
    result = connection.execute(statement).fetchone()
    connection.close()
    return result

# find out which collections are set as externally published
def get_collection_published_status():
    connection = db_engine.connect()
    select = "SELECT id, published FROM publication_collection WHERE deleted = 0;"
    statement = text(select).bindparams()
    result = []
    for row in connection.execute(statement).fetchall():
        result.append(dict(row))
    connection.close()
    return result

# make sure the given combo of collection id and
# publication id exists, and check the publication's
# published status
def get_publication_published_status(collection_id, publication_id):
    connection = db_engine.connect()
    select = "SELECT published FROM publication WHERE publication_collection_id = :pub_coll_id AND id = :p_id;"
    statement = text(select).bindparams(pub_coll_id=collection_id, p_id=publication_id)
    result = connection.execute(statement).fetchone()
    connection.close()
    if result is None:
        return None
    else:
        return result["published"]

# get the file path for the reading text
def get_est_file_path(publication_id, language):
    connection = db_engine.connect()
    select = "SELECT tt.text AS file FROM publication AS p LEFT JOIN translation_text AS tt ON tt.translation_id = p.translation_id AND tt.language = :lang AND tt.field_name = 'original_filename' WHERE p.id = :p_id AND p.deleted = 0;"
    statement = text(select).bindparams(p_id=publication_id, lang=language)
    result = connection.execute(statement).fetchone()
    connection.close()
    if result is None:
        return None
    else:
        return result["file"]

# get manuscript/transcription data
def get_ms_data(publication_id):
    connection = db_engine.connect()
    select = "SELECT id, name AS title, original_filename, original_language AS language, deleted FROM publication_manuscript WHERE publication_id = :p_id;"
    statement = text(select).bindparams(p_id=publication_id)
    result = connection.execute(statement).fetchone()
    connection.close()
    return result

# find out if the publication has been deleted
def publication_deleted(publication_id):
    connection = db_engine.connect()
    select = "SELECT deleted FROM publication WHERE id = :p_id;"
    statement = text(select).bindparams(p_id=publication_id)
    result = connection.execute(statement).fetchone()
    connection.close()
    return result

# get data for all collections (serving the page called "content")
def get_collections_data(language, published_collections):
    connection = db_engine.connect()
    if language == "sv":
        select = "SELECT id, name AS title, publication_collection_introduction_id, publication_collection_title_id, published FROM publication_collection WHERE id = ANY(:pub_coll) ORDER BY id;"
    if language == "fi":
        select = "SELECT c.id, text AS title, publication_collection_introduction_id, publication_collection_title_id, published FROM publication_collection AS c, translation_text AS tt WHERE c.translation_id = tt.translation_id AND c.id = ANY(:pub_coll) ORDER BY id;"
    statement = text(select).bindparams(pub_coll=published_collections)
    result = []
    for row in connection.execute(statement).fetchall():
        result.append(dict(row))
    connection.close()
    return result

# get facsimile data
def get_facsimile_data(publication_id, published_collections):
    connection = db_engine.connect()
    select = "SELECT p.id AS id, p.id AS publication_id, p.publication_collection_id, p.published, fc.id AS publication_facsimile_collection_id, f.id AS publication_facsimile_id, title, number_of_pages, number_of_pages AS last_page, start_page_number, start_page_number AS first_page, folder_path, external_url, priority FROM publication_facsimile AS f, publication_facsimile_collection AS fc, publication AS p WHERE p.id = :p_id AND p.id = f.publication_id AND fc.id = f.publication_facsimile_collection_id AND p.publication_collection_id = ANY(:pub_coll) AND f.deleted = 0 AND fc.deleted = 0 AND p.deleted = 0 ORDER BY priority;"
    statement = text(select).bindparams(p_id=publication_id, pub_coll=published_collections)
    result = []
    for row in connection.execute(statement).fetchall():
        result.append(dict(row))
    connection.close()
    return result

# get the file path for the introduction
def get_intro_file_path(collection_id, language):
    connection = db_engine.connect()
    if language == "sv":
        select = "SELECT original_filename AS file FROM publication_collection_introduction AS ci, publication_collection AS c WHERE c.id = :pub_coll_id AND c.publication_collection_introduction_id = ci.id;"
    if language == "fi":
        select = "SELECT text AS file FROM publication_collection_introduction AS ci, publication_collection AS c, translation_text AS tt WHERE c.id = :pub_coll_id AND c.publication_collection_introduction_id = ci.id AND ci.translation_id = tt.translation_id;"
    statement = text(select).bindparams(pub_coll_id=collection_id)
    result = connection.execute(statement).fetchone()
    connection.close()
    if result is None:
        return None
    else:
        return result["file"]

# get the file path for the title page
def get_title_file_path(collection_id, language):
    connection = db_engine.connect()
    if language == "sv":
        select = "SELECT original_filename AS file FROM publication_collection_title AS ct, publication_collection AS c WHERE c.id = :pub_coll_id AND c.publication_collection_title_id = ct.id;"
    if language == "fi":
        select = "SELECT text AS file FROM publication_collection_title AS ct, publication_collection AS c, translation_text AS tt WHERE c.id = :pub_coll_id AND c.publication_collection_title_id = ct.id AND ct.translation_id = tt.translation_id;"
    statement = text(select).bindparams(pub_coll_id=collection_id)
    result = connection.execute(statement).fetchone()
    connection.close()
    if result is None:
        return None
    else:
        return result["file"]

# get metadata for the publication
def get_publication_metadata(publication_id, language, published_collections):
    connection = db_engine.connect()
    if language == "sv":
        select = """SELECT
                MAX(p.id) AS id,
                MAX(pm.id) AS manuscript_id,
                MAX(p.publication_collection_id) AS publication_collection_id,
                MAX(p.original_publication_date) AS publication_date,
                MAX(p.genre) AS document_type,
                MAX(p.published_by) AS published_by,
                MAX(p.original_language) AS original_language,
                MAX(p.archive_signum) AS publication_archive_info,
                subject.id AS person_id,
                MAX(CASE
                    WHEN tt.language = :lang AND tt.field_name = 'name' THEN tt.text
                END) AS publication_title,
                MAX(CASE
                    WHEN tt.language = :lang AND tt.field_name = 'subtitle' THEN tt.text
                END) AS publication_subtitle,
                CASE
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') AND NOT EXISTS
                        (SELECT subject_id FROM publication AS p
                        LEFT JOIN event_occurrence AS eo ON p.id = eo.publication_id
                        LEFT JOIN event_connection AS ec ON eo.event_id = ec.event_id
                        WHERE (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND p.id = :p_id)
                    THEN 'Leo Mechelin'
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') THEN subject.full_name
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') THEN subject.full_name
                END AS sender,
                CASE
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') AND NOT EXISTS
                        (SELECT subject_id FROM publication AS p
                        LEFT JOIN event_occurrence AS eo ON p.id = eo.publication_id
                        LEFT JOIN event_connection AS ec ON eo.event_id = ec.event_id
                        WHERE (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND p.id = :p_id)
                    THEN 'Mechelin'
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') THEN subject.last_name
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') THEN subject.last_name
                END AS sender_last_name,
                CASE
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND NOT EXISTS
                        (SELECT subject_id FROM publication AS p
                        LEFT JOIN event_occurrence AS eo ON p.id = eo.publication_id
                        LEFT JOIN event_connection AS ec ON eo.event_id = ec.event_id
                        WHERE (ec.type = 'received letter' OR ec.type = 'received telegram') AND p.id = :p_id)
                    THEN 'Leo Mechelin'
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') THEN subject.full_name
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') THEN subject.full_name
                END AS recipient,
                CASE
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND NOT EXISTS
                        (SELECT subject_id FROM publication AS p
                        LEFT JOIN event_occurrence AS eo ON p.id = eo.publication_id
                        LEFT JOIN event_connection AS ec ON eo.event_id = ec.event_id
                        WHERE (ec.type = 'received letter' OR ec.type = 'received telegram') AND p.id = :p_id)
                    THEN 'Mechelin'
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') THEN subject.last_name
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') THEN subject.last_name
                END AS recipient_last_name,
                CASE
                    WHEN eo.type IS NULL THEN 'Leo Mechelin'
                    WHEN eo.type NOT LIKE '%letter%' AND eo.type NOT LIKE '%telegram%' AND subject_id = 1 THEN 'Leo Mechelin'
                    WHEN eo.type NOT LIKE '%letter%' AND eo.type NOT LIKE '%telegram%' AND subject_id != 1 THEN subject.full_name
                END AS author,
                CASE
                    WHEN eo.type IS NULL THEN 'Mechelin'
                    WHEN eo.type NOT LIKE '%letter%' AND eo.type NOT LIKE '%telegram%' AND subject_id = 1 THEN 'Mechelin'
                    WHEN eo.type NOT LIKE '%letter%' AND eo.type NOT LIKE '%telegram%' AND subject_id != 1 THEN subject.last_name
                END AS author_last_name,
                MAX(CASE
					WHEN f.priority = 1 THEN f.publication_facsimile_collection_id
				END) AS facs_coll_id,
                MAX(CASE
					WHEN f.priority = 1 AND f.type = 0 THEN fc.title
				END) AS facsimile_title,
                MAX(CASE
					WHEN f.priority = 1 THEN fc.description
				END) AS archive_info,
                MAX(CASE
                    WHEN f.priority = 1 THEN fc.number_of_pages
                END) AS number_of_images,
                MAX(CASE
                    WHEN f.priority = 1 THEN fc.page_comment
                END) AS image_number_info,
                MAX(CASE
                    WHEN f.priority = 1 THEN fc.external_url
                END) AS external_url,
                contribution.text_language AS translated_into,
                CASE
                    WHEN contributor_id IS NOT NULL THEN CONCAT(contributor.first_name, ' ', contributor.last_name)
                END AS translator
                FROM publication AS p
                LEFT JOIN
                    publication_manuscript AS pm ON p.id = pm.publication_id AND pm.deleted = 0
                LEFT JOIN
                    event_occurrence AS eo ON p.id = eo.publication_id AND eo.deleted = 0
                LEFT JOIN
                    publication_facsimile AS f ON p.id = f.publication_id AND f.deleted = 0
                LEFT JOIN
                    publication_facsimile_collection AS fc ON f.publication_facsimile_collection_id = fc.id AND fc.deleted = 0
                LEFT JOIN
                    event_connection AS ec ON eo.event_id = ec.event_id AND ec.deleted = 0
                LEFT JOIN
                    subject ON ec.subject_id = subject.id
                LEFT JOIN
                    translation_text AS tt ON (p.translation_id = tt.translation_id AND tt.field_name = 'name') OR (p.translation_id = tt.translation_id AND tt.field_name = 'subtitle') AND tt.language = :lang AND tt.deleted = 0
                LEFT JOIN
                    contribution ON p.id = contribution.publication_id AND contribution.deleted = 0
                LEFT JOIN
                    contributor ON contribution.contributor_id = contributor.id
                WHERE
                    p.deleted = 0 AND p.id = :p_id AND p.publication_collection_id = ANY(:pub_coll)
                GROUP BY
                    person_id, sender, sender_last_name, recipient, recipient_last_name, author, author_last_name, translated_into, translator;"""
    if language == "fi":
        select = """SELECT
                MAX(p.id) AS id,
                MAX(pm.id) AS manuscript_id,
                MAX(p.publication_collection_id) AS publication_collection_id,
                MAX(p.original_publication_date) AS publication_date,
                MAX(p.genre) AS document_type,
                MAX(p.published_by) AS published_by,
                MAX(p.original_language) AS original_language,
                MAX(p.archive_signum) AS publication_archive_info,
                subject.id AS person_id,
                MAX(CASE
                    WHEN tt.language = :lang AND tt.field_name = 'name' THEN tt.text
                END) AS publication_title,
                MAX(CASE
                    WHEN tt.language = :lang AND tt.field_name = 'subtitle' THEN tt.text
                END) AS publication_subtitle,
                CASE
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') AND NOT EXISTS
                        (SELECT subject_id FROM publication AS p
                        LEFT JOIN event_occurrence AS eo ON p.id = eo.publication_id
                        LEFT JOIN event_connection AS ec ON eo.event_id = ec.event_id
                        WHERE (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND p.id = :p_id)
                    THEN 'Leo Mechelin'
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND subject.translation_id IS NULL THEN subject.full_name
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND subject.translation_id IS NOT NULL AND tt.field_name = 'full_name' THEN tt.text
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND subject.translation_id IS NULL THEN subject.full_name
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND subject.translation_id IS NOT NULL AND tt.field_name = 'full_name' THEN tt.text
                END AS sender,
                CASE
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') AND NOT EXISTS
                        (SELECT subject_id FROM publication AS p
                        LEFT JOIN event_occurrence AS eo ON p.id = eo.publication_id
                        LEFT JOIN event_connection AS ec ON eo.event_id = ec.event_id
                        WHERE (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND p.id = :p_id)
                    THEN 'Mechelin'
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND subject.translation_id IS NULL THEN subject.last_name
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND subject.translation_id IS NOT NULL AND tt.field_name = 'last_name' THEN tt.text
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND subject.translation_id IS NULL THEN subject.last_name
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND subject.translation_id IS NOT NULL AND tt.field_name = 'last_name' THEN tt.text
                END AS sender_last_name,
                CASE
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND NOT EXISTS
                        (SELECT subject_id FROM publication AS p
                        LEFT JOIN event_occurrence AS eo ON p.id = eo.publication_id
                        LEFT JOIN event_connection AS ec ON eo.event_id = ec.event_id
                        WHERE (ec.type = 'received letter' OR ec.type = 'received telegram') AND p.id = :p_id)
                    THEN 'Leo Mechelin'
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') AND subject.translation_id IS NULL THEN subject.full_name
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') AND subject.translation_id IS NOT NULL AND tt.field_name = 'full_name' THEN tt.text
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') AND subject.translation_id IS NULL THEN subject.full_name
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') AND subject.translation_id IS NOT NULL AND tt.field_name = 'full_name' THEN tt.text
                END AS recipient,
                CASE
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'sent letter' OR ec.type = 'sent telegram') AND NOT EXISTS
                        (SELECT subject_id FROM publication AS p
                        LEFT JOIN event_occurrence AS eo ON p.id = eo.publication_id
                        LEFT JOIN event_connection AS ec ON eo.event_id = ec.event_id
                        WHERE (ec.type = 'received letter' OR ec.type = 'received telegram') AND p.id = :p_id)
                    THEN 'Mechelin'
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') AND subject.translation_id IS NULL THEN subject.last_name
                    WHEN (eo.type = 'received letter' OR eo.type = 'received telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') AND subject.translation_id IS NOT NULL AND tt.field_name = 'last_name' THEN tt.text
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') AND subject.translation_id IS NULL THEN subject.last_name
                    WHEN (eo.type = 'sent letter' OR eo.type = 'sent telegram') AND (ec.type = 'received letter' OR ec.type = 'received telegram') AND subject.translation_id IS NOT NULL AND tt.field_name = 'last_name' THEN tt.text
                END AS recipient_last_name,
                CASE
                    WHEN eo.type IS NULL THEN 'Leo Mechelin'
                    WHEN eo.type NOT LIKE '%letter%' AND eo.type NOT LIKE '%telegram%' AND subject_id = 1 THEN 'Leo Mechelin'
                    WHEN eo.type NOT LIKE '%letter%' AND eo.type NOT LIKE '%telegram%' AND subject_id != 1 AND subject.translation_id IS NULL THEN subject.full_name
                    WHEN eo.type NOT LIKE '%letter%' AND eo.type NOT LIKE '%telegram%' AND subject_id != 1 AND subject.translation_id IS NOT NULL AND tt.field_name = 'full_name' THEN tt.text
                END AS author,
                CASE
                    WHEN eo.type IS NULL THEN 'Mechelin'
                    WHEN eo.type NOT LIKE '%letter%' AND eo.type NOT LIKE '%telegram%' AND subject_id = 1 THEN 'Mechelin'
                    WHEN eo.type NOT LIKE '%letter%' AND eo.type NOT LIKE '%telegram%' AND subject_id != 1 AND subject.translation_id IS NULL THEN subject.last_name
                    WHEN eo.type NOT LIKE '%letter%' AND eo.type NOT LIKE '%telegram%' AND subject_id != 1 AND subject.translation_id IS NOT NULL AND tt.field_name = 'last_name' THEN tt.text
                END AS author_last_name,
                MAX(CASE
					WHEN f.priority = 1 THEN f.publication_facsimile_collection_id
				END) AS facs_coll_id,
                MAX(CASE
					WHEN f.priority = 1 AND f.type = 0 THEN fc.title
				END) AS facsimile_title,
                MAX(CASE
					WHEN f.priority = 1 THEN fc.description
				END) AS archive_info,
                MAX(CASE
                    WHEN f.priority = 1 THEN fc.number_of_pages
                END) AS number_of_images,
                MAX(CASE
                    WHEN f.priority = 1 THEN fc.page_comment
                END) AS image_number_info,
                MAX(CASE
                    WHEN f.priority = 1 THEN fc.external_url
                END) AS external_url,
                contribution.text_language AS translated_into,
                CASE
                    WHEN contributor_id IS NOT NULL THEN CONCAT(contributor.first_name, ' ', contributor.last_name)
                END AS translator
                FROM publication AS p
                LEFT JOIN
                    publication_manuscript AS pm ON p.id = pm.publication_id AND pm.deleted = 0
                LEFT JOIN
                    event_occurrence AS eo ON p.id = eo.publication_id AND eo.deleted = 0
                LEFT JOIN
                    publication_facsimile AS f ON p.id = f.publication_id AND f.deleted = 0
                LEFT JOIN
                    publication_facsimile_collection AS fc ON f.publication_facsimile_collection_id = fc.id AND fc.deleted = 0
                LEFT JOIN
                    event_connection AS ec ON eo.event_id = ec.event_id AND ec.deleted = 0
                LEFT JOIN
                    subject ON ec.subject_id = subject.id
                LEFT JOIN
                    translation_text AS tt ON (p.translation_id = tt.translation_id AND tt.field_name = 'name') OR (p.translation_id = tt.translation_id AND tt.field_name = 'subtitle') OR (subject.translation_id = tt.translation_id AND tt.field_name = 'full_name') OR (subject.translation_id = tt.translation_id AND tt.field_name = 'last_name') AND tt.language = :lang AND tt.deleted = 0
                LEFT JOIN
                    contribution ON p.id = contribution.publication_id AND contribution.deleted = 0
                LEFT JOIN
                    contributor ON contribution.contributor_id = contributor.id
                WHERE
                    p.deleted = 0 AND p.id = :p_id AND p.publication_collection_id = ANY(:pub_coll)
                GROUP BY
                    person_id, sender, sender_last_name, recipient, recipient_last_name, author, author_last_name, translated_into, translator;"""
    statement = text(select).bindparams(p_id=publication_id, lang=language, pub_coll=published_collections)
    result = []
    # combine tuples containing info for the same person
    # sorting names in functions using this query result
    # is easier if all name info is in the same tuple
    PERSON_ID_INDEX = 8
    for row in connection.execute(statement).fetchall():
        if row and row[PERSON_ID_INDEX] is not None:
            person_id = row[PERSON_ID_INDEX]
            # check if there already is an entry for this person_id
            existing_entry_index = next((i for i, entry in enumerate(result) if entry.get("person_id") == person_id), None)
            if existing_entry_index is not None:
                # update the existing entry with missing information
                existing_entry = result[existing_entry_index]
                for key, value in row.items():
                    if existing_entry[key] is None and value is not None:
                        existing_entry[key] = value
                    # don't lose tuples by only updating None values in existing tuples
                    # other values may differ, and then the tuple should be appended
                    # with its missing information updated first, and the differing
                    # information intact
                    elif existing_entry[key] is not None and value is not None and existing_entry[key] != value:
                        result.append(dict(row))
            else:
                # create a new entry if person_id doesn't already exist in the result
                result.append(dict(row))
        else:
            # if person_id is None: append the tuple anyway
            # LM as author/sender/recipient is only registered with person_id
            # in cases where he's the co-author etc., otherwise not
            # and we need these tuples too as part of the result
            result.append(dict(row))
    connection.close()
    return result

# get facsimile data if there's more than one facsimile unit
# for this publication
def get_alternative_facsimiles(publication_id):
    connection = db_engine.connect()
    select = "SELECT publication_facsimile_collection_id AS facs_coll_id, priority, title AS facsimile_title, description AS archive_info, number_of_pages AS number_of_images, page_comment AS image_number_info, external_url FROM publication_facsimile AS f, publication_facsimile_collection AS fc WHERE f.publication_id = :p_id AND f.publication_facsimile_collection_id = fc.id AND priority > 1 AND f.deleted = 0 AND fc.deleted = 0;"
    statement = text(select).bindparams(p_id=publication_id)
    result = []
    for row in connection.execute(statement).fetchall():
        result.append(dict(row))
    connection.close()
    return result

# get person data for a single person
def get_subject_data(subject_id, language):
    connection = db_engine.connect()
    if language == "sv":
        select = "SELECT id, first_name, last_name, preposition, full_name, description, date_born, date_deceased, alias, previous_last_name FROM subject WHERE id = :s_id AND deleted = 0;"
    if language == "fi":
        select = """SELECT subject.id,
            MAX(CASE
                WHEN subject.translation_id IS NULL THEN first_name
                WHEN subject.translation_id IS NOT NULL AND field_name = 'first_name' THEN tt.text
            END) AS first_name,
            MAX(CASE
                WHEN subject.translation_id IS NULL THEN last_name
                WHEN subject.translation_id IS NOT NULL AND field_name = 'last_name' THEN tt.text
            END) AS last_name,
            MAX(CASE
                WHEN subject.translation_id IS NULL THEN preposition
                WHEN subject.translation_id IS NOT NULL AND field_name = 'preposition' THEN tt.text
            END) AS preposition,
            MAX(CASE
                WHEN subject.translation_id IS NULL THEN full_name
                WHEN subject.translation_id IS NOT NULL AND field_name = 'full_name' THEN tt.text
            END) AS full_name,
                description, date_born, date_deceased, alias, previous_last_name
            FROM subject
            LEFT JOIN
                translation_text AS tt ON subject.translation_id = tt.translation_id AND tt.deleted = 0
            WHERE subject.id = :s_id AND subject.deleted = 0 GROUP BY subject.id;"""
    statement = text(select).bindparams(s_id=subject_id)
    result = connection.execute(statement).fetchone()
    connection.close()
    return result

# get person data for the whole index of persons
def get_persons_data(language):
    connection = db_engine.connect()
    if language == "sv":
        select = "SELECT id, first_name, last_name, preposition, full_name, description, date_born, date_deceased, alias, previous_last_name FROM subject WHERE deleted = 0 ORDER BY last_name;"
    if language == "fi":
        select = """SELECT subject.id,
            MAX(CASE
                WHEN subject.translation_id IS NULL THEN first_name
                WHEN subject.translation_id IS NOT NULL AND field_name = 'first_name' THEN tt.text
            END) AS first_name,
            MAX(CASE
                WHEN subject.translation_id IS NULL THEN last_name
                WHEN subject.translation_id IS NOT NULL AND field_name = 'last_name' THEN tt.text
            END) AS last_name,
            MAX(CASE
                WHEN subject.translation_id IS NULL THEN preposition
                WHEN subject.translation_id IS NOT NULL AND field_name = 'preposition' THEN tt.text
            END) AS preposition,
            MAX(CASE
                WHEN subject.translation_id IS NULL THEN full_name
                WHEN subject.translation_id IS NOT NULL AND field_name = 'full_name' THEN tt.text
            END) AS full_name,
                description, date_born, date_deceased, alias, previous_last_name
            FROM subject
            LEFT JOIN
                translation_text AS tt ON (subject.translation_id = tt.translation_id AND tt.field_name = 'full_name') OR (subject.translation_id = tt.translation_id AND tt.field_name = 'first_name') OR (subject.translation_id = tt.translation_id AND tt.field_name = 'last_name') OR (subject.translation_id = tt.translation_id AND tt.field_name = 'preposition') AND tt.deleted = 0
            WHERE subject.deleted = 0 GROUP BY subject.id ORDER BY last_name;"""
    statement = text(select).bindparams()
    result = []
    result = connection.execute(statement).fetchall()
    connection.close()
    return result

# get the reference text and a possible urn/permanent identifier
# for the publication
def get_urn_data(url):
    url_without_pub_id = re.sub(r"\d*$|\d*/$", "", url)
    connection = db_engine.connect()
    select = "SELECT id, urn, url, reference_text FROM urn_lookup WHERE url = :url AND deleted = 0;"
    statement = text(select).bindparams(url=url_without_pub_id)
    result = connection.execute(statement).fetchone()
    connection.close()
    return result

# get collection data for the text download
# for the collection
def get_collection_data(collection_id, language):
    connection = db_engine.connect()
    if language == "sv":
        select = "SELECT id, name, publication_collection_introduction_id, publication_collection_title_id, published FROM publication_collection WHERE id = :pub_coll_id;"
    if language == "fi":
        select = "SELECT c.id, text AS name, publication_collection_introduction_id, publication_collection_title_id, published FROM publication_collection AS c, translation_text AS tt WHERE c.translation_id = tt.translation_id AND c.id = :pub_coll_id;"
    statement = text(select).bindparams(pub_coll_id=collection_id)
    result = connection.execute(statement).fetchone()
    connection.close()
    return result

# get data for all publications of a collection
def get_publications_data(collection_id, language):
    connection = db_engine.connect()
    select = """SELECT
        p.id AS publication_id, publication_group_id,
        CASE
            WHEN tt.field_name = 'name' THEN tt.text
        END AS publication_title,
        CASE
            WHEN tt.field_name = 'subtitle' THEN tt.text
        END AS publication_subtitle,
        published_by, genre AS document_type, original_language, original_publication_date AS publication_date, archive_signum AS archive_info
        FROM publication AS p
        LEFT JOIN
                translation_text AS tt ON (p.translation_id = tt.translation_id AND tt.field_name = 'name') OR (p.translation_id = tt.translation_id AND tt.field_name = 'subtitle') AND tt.language = :lang AND tt.deleted = 0
        WHERE p.deleted = 0 AND p.publication_collection_id = :pub_coll_id AND tt.language = :lang
        ORDER BY p.id;"""
    statement = text(select).bindparams(pub_coll_id=collection_id, lang=language)
    result = []
    for row in connection.execute(statement).fetchall():
        result.append(dict(row))
    connection.close()
    return result

# get publication data for the download texts feature
def get_publication_data(publication_id, language):
    connection = db_engine.connect()
    select = """SELECT
        publication_group_id, tt.text AS original_filename
        FROM publication AS p
        LEFT JOIN
                translation_text AS tt ON p.translation_id = tt.translation_id AND tt.field_name = 'original_filename' AND tt.language = :lang AND tt.deleted = 0
        WHERE tt.language = :lang AND p.id = :p_id"""
    statement = text(select).bindparams(p_id=publication_id, lang=language)
    result = connection.execute(statement).fetchone()
    connection.close()
    return result

# get ms data for all ms:s for a publication
def get_ms_list_data(publication_id):
    connection = db_engine.connect()
    select ="SELECT pm.id, pm.name, type, pm.archive_signum AS archive_info, pm.original_language AS language, pm.original_filename FROM publication AS p, publication_manuscript AS pm WHERE p.id = publication_id AND p.id = :p_id AND pm.deleted = 0;"
    statement = text(select).bindparams(p_id=publication_id)
    result = connection.execute(statement).fetchone()
    connection.close()
    return result