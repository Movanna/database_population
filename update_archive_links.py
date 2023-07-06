# This script updates url values connected to facsimiles
# (i.e. images units) in table publication_facsimile_collection.

# The National Archives updated their online digital archive services
# and discontinued the old service. This project had thousands of links
# to images in the old archive, and consequently, those links went dead
# and needed to be replaced with new url:s to the new service.
# This project also had even more publications with no links at all,
# because in the transition phase there was initially no certainty of
# how they should be constructed for the new service.

# This script thus fixes missing links and swaps the already existing
# old ones into their new equivalents.

import psycopg2
import re

conn_db = psycopg2.connect(
    host="",
    database="",
    user="",
    port="",
    password=""
)
cursor = conn_db.cursor()

# fetch items possibly in need of a new url
def fetch_items_needing_update():
    fetch_query = """SELECT id, description FROM publication_facsimile_collection WHERE external_url IS NULL"""
    cursor.execute(fetch_query)
    missing_links = cursor.fetchall()
    fetch_query = """SELECT id, description FROM publication_facsimile_collection WHERE external_url LIKE '%astiaUi%'"""
    cursor.execute(fetch_query)
    old_links = cursor.fetchall()
    return missing_links, old_links

# only add/update url:s for entries that have a certain type
# of archive signum and are from the National Archives
# otherwise the new url obviously won't work
def get_signum_and_update_url(needs_url_update, new_url_base):
    for list in needs_url_update:
        for tuple in list:
            pub_coll_id = tuple[0]
            archive_signums = tuple[1]
            # look for the correct signum/id
            search_string = re.compile(r"\d{10}")
            match_string = re.search(search_string, archive_signums)
            # if no id in this form could be found, this item isn't
            # from the National Archives or is lacking needed info
            # and should be ignored in the update operation
            if not match_string:
                continue
            # the new url:s are easy to construct if you know the correct signum
            # (we actually started with an even older signum, but luckily
            # the archive provided a list of old and new signums, so that got
            # sorted out earlier on)
            else:
                unit_id = match_string.group(0)
                new_url = new_url_base + unit_id
                print(str(pub_coll_id) + ": " + new_url)
                update_external_url(pub_coll_id, new_url)

def update_external_url(pub_coll_id, new_url):
    update_query = """UPDATE publication_facsimile_collection SET external_url = %s WHERE id = %s"""
    values_to_insert = (new_url, pub_coll_id)
    cursor.execute(update_query, values_to_insert)

def main():
    missing_links, old_links = fetch_items_needing_update()
    new_url_base = "https://astia.narc.fi/uusiastia/digitarkastelu.html?id="
    needs_url_update = [missing_links, old_links]
    get_signum_and_update_url(needs_url_update, new_url_base)
    conn_db.commit()
    print("Table publication_facsimile_collection updated with new url values.")
    conn_db.close()
    cursor.close()

main()