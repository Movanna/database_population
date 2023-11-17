# A Flask app is used to build the website's API.
# This script creates the endpoints for the API. 
# There are a couple of more endpoints, but since
# I didn't write the code for them myself, I excluded them.

# The live API endpoints can be found at https://leomechelin.fi 
# + what's stated in the corresponding @app.route() decorator,
# where <project> is leomechelin. Examples:
# https://leomechelin.fi/api/leomechelin/publications/97/metadata/sv
# https://leomechelin.fi/api/leomechelin/text/downloadable/txt/1/100/est-i18n/sv
# https://leomechelin.fi/api/leomechelin/text/1/100/ms
# https://leomechelin.fi/api/leomechelin/subject/1/sv

from flask import Flask, jsonify, safe_join, abort, request
from flask_cors import CORS, cross_origin
from urllib.parse import unquote
# The script uses the website versions of the text transformation
# scripts in my repo transform_texts. The transform function is
# basically the same as the main function in those scripts,
# only that it doesn't create an html file but returns the content
# as a string, which is then part of what the endpoint returns.
from src.replaces_xslt import transform
from src.transform_ms import transform as transform_ms
from src.transform_ms_normalized import transform as transform_ms_normalized
from src.transform_downloadable_xml import transform as transform_downloadable_xml
from src.transform_downloadable_txt import transform_to_txt
# These are the database queries the endpoints use
import src.endpoint_queries as queries

app = Flask(__name__)
CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

# collections of texts can be set as internally or externally 
# published in the db, and this value is then used for showing
# different content on the internal and the external site
# the API will serve different content depending on where
# the request comes from
def get_published_collections(project):
    # the given project value obviously has to be this project
    if project != "leomechelin":
        return None
    show_internally_published = False
    published_collections = []
    origin = request.environ.get("HTTP_ORIGIN")
    if origin is not None and (origin == "https://[internal_site]" or origin == "http://localhost:4200" or origin == "http://localhost:4201"):
        show_internally_published = True
    if show_internally_published is True:
        published_collections = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    else:
        collection_status = queries.get_collection_published_status(project)
        for collection in collection_status:
            collection_id = collection["id"]
            published = collection["published"]
            if published == 2:
                published_collections.append(collection_id)
    return published_collections

# endpoints for the manuscript/transcription column
# the one with ms_id used for download
@app.route("/api/<project>/text/<collection_id>/<publication_id>/ms")
@app.route("/api/<project>/text/<collection_id>/<publication_id>/ms/<ms_id>")
@cross_origin()
def get_ms(project, collection_id, publication_id, ms_id=None):
    published_collections = get_published_collections(project)
    # None means that the given project value was wrong
    if published_collections is None:
        abort(404)
    publication_published_status = queries.get_publication_published_status(collection_id, publication_id)
    # if status is None, then the given combo of collection id 
    # and publication id doesn't exist
    if publication_published_status is None:
        abort(404)
    if published_collections != [] and int(collection_id) in published_collections and (publication_published_status == 1 or publication_published_status == 2):
        ms_data = queries.get_ms_data(publication_id)
        # if the publication simply doesn't have an ms
        # and only consists of the reading text
        empty_data = {
            "id": "{}_{}".format(collection_id, publication_id),
            "manuscripts": []
        }
        if ms_data is None:
            data = empty_data
        else:
            id = ms_data[0]
            title = ms_data[1]
            file = ms_data[2]
            language = ms_data[3]
            deleted = ms_data[4]
            if ms_id is not None:
                # if an ms_id was provided and it was wrong
                if str(id) != str(ms_id):
                    abort(404)
            if deleted == 0:
                data = {
                    "id": "{}_{}".format(collection_id, publication_id),
                    "manuscripts": [{
                        "id": id,
                        "language": language,
                        "title": title,
                        "original_filename": file,
                        "manuscript_changes": transform_ms(file, language),
                        "manuscript_normalized": transform_ms_normalized(file, language)
                    }]
                }
            # this ms has been deleted
            # let's find out if it's just the ms or the whole publication
            else:
                no_publication = queries.publication_deleted(publication_id)
                if no_publication[0] == 1:
                    data = {
                        "id": "{}_{}".format(collection_id, publication_id),
                        "manuscripts": [{
                            "id": id,
                            "manuscript_changes": "",
                            "manuscript_normalized": ""
                        }]
                    }
                else:
                    data = empty_data
        response = jsonify(data)
        return response, 200
    else:
        message = "Content is not yet published."
        return jsonify({
            "id": "{}_{}_".format(collection_id, publication_id),
            "error": message
        }), 403

# endpoint for download of reading texts
# two downloadable formats: txt, xml
@app.route("/api/<project>/text/downloadable/<format>/<collection_id>/<publication_id>/est-i18n/<language>")
@cross_origin()
def get_downloadable_text(project, format, collection_id, publication_id, language):
    published_collections = get_published_collections(project)
    # None means that the given project value was wrong
    if published_collections is None:
        abort(404)
    publication_published_status = queries.get_publication_published_status(collection_id, publication_id)
    no_publication = queries.publication_deleted(publication_id)
    # if status is None, then the given combo of collection id 
    # and publication id doesn't exist
    # and if the publication is deleted, there's nothing to fetch
    if publication_published_status is None or no_publication[0] == 1:
        abort(404)
    if published_collections != [] and int(collection_id) in published_collections and (publication_published_status == 1 or publication_published_status == 2):
        file_path = queries.get_est_file_path(publication_id, language)
        if file_path is None:
            data = {
                "id": "{}_{}_est".format(collection_id, publication_id),
                "content": "",
                "language": language
            }
        else:
            est_or_ms = "est"
            if format == "txt":
                file_path = "./" + file_path
                content = transform_to_txt(file_path, est_or_ms)
                data = {
                    "id": "{}_{}_{}_est".format(collection_id, publication_id, language),
                    "content": content,
                    "language": language
                }
                metadata = queries.get_publication_metadata(publication_id, language, published_collections)
                if metadata != []:
                    bibl_data = create_bibl_data(metadata, publication_id, language, est_or_ms)
                    # don't overwrite the id from the data dict above when merging dicts
                    bibl_data.pop("id")
                    data.update(bibl_data)
                    # if this text's language value isn't in orig_lang_abbr
                    # then there's a separate manuscript file (or no manuscript file at all)
                    # and we shouldn't connect that manuscript_id to this text
                    if language not in data.get("orig_lang_abbr", []):
                        data.pop("manuscript_id")
            elif format == "xml":
                metadata = queries.get_publication_metadata(publication_id, language, published_collections)
                if metadata != []:
                    bibl_data = create_bibl_data(metadata, publication_id, language, est_or_ms)
                else:
                    bibl_data = None
                content = transform_downloadable_xml(file_path, language, bibl_data, est_or_ms)
                data = {
                    "id": "{}_{}_{}_est".format(collection_id, publication_id, language),
                    "content": content,
                    "language": language
                }
            # if given format is non-existent
            else:
                abort(404)
        response = jsonify(data)
        return response, 200
    else:
        message = "Content is not yet published."
        return jsonify({
            "id": "{}_{}_".format(collection_id, publication_id),
            "language": language,
            "error": message
        }), 403

# endpoint for download of ms/transcription
# two downloadable formats: txt, xml 
@app.route("/api/<project>/text/downloadable/<format>/<collection_id>/<publication_id>/ms/<ms_id>")
@cross_origin()
def get_downloadable_text_for_ms(project, format, collection_id, publication_id, ms_id):
    published_collections = get_published_collections(project)
    # None means that the given project value was wrong
    if published_collections is None:
        abort(404)
    publication_published_status = queries.get_publication_published_status(collection_id, publication_id)
    no_publication = queries.publication_deleted(publication_id)
    # if status is None, then the given combo of collection id 
    # and publication id doesn't exist
    # and if the publication is deleted, there's nothing to fetch
    if publication_published_status is None or no_publication[0] == 1:
        abort(404)
    if published_collections != [] and int(collection_id) in published_collections and (publication_published_status == 1 or publication_published_status == 2):
        ms_data = queries.get_ms_data(publication_id)
        id = ms_data[0]
        file_path = ms_data[2]
        original_language = ms_data[3]
        deleted = ms_data[4]
        # if the given ms_id was wrong
        if str(id) != str(ms_id):
            abort(404)
        # if the publication simply doesn't have an ms
        # and only consists of the reading text
        if ms_data is None or deleted == 1:
            data = {
                "id": "{}_{}_{}_ms".format(collection_id, publication_id, ms_id),
                "content": "",
            }
        else:
            est_or_ms = "ms"
            if "sv" in original_language:
                language = "sv"
            elif "fi" in original_language:
                language = "fi"
            else:
                language = "sv"
            if format == "txt":
                file_path = "./" + file_path
                content = transform_to_txt(file_path, est_or_ms)
                data = {
                    "id": "{}_{}_{}_ms".format(collection_id, publication_id, ms_id),
                    "content": content,
                    "language": original_language
                }
                metadata = queries.get_publication_metadata(publication_id, language, published_collections)
                if metadata != []:
                    bibl_data = create_bibl_data(metadata, publication_id, language, est_or_ms)
                    # don't overwrite the id from the data dict above when merging dicts
                    # also delete translations since this is the original text
                    bibl_data.pop("id")
                    bibl_data.pop("translations")
                    data.update(bibl_data)
            elif format == "xml":
                metadata = queries.get_publication_metadata(publication_id, language, published_collections)
                if metadata != []:
                    bibl_data = create_bibl_data(metadata, publication_id, language, est_or_ms)
                else:
                    bibl_data = None
                content = transform_downloadable_xml(file_path, language, bibl_data, est_or_ms)
                data = {
                    "id": "{}_{}_{}_ms".format(collection_id, publication_id, ms_id),
                    "content": content,
                    "language": original_language
                }
            # if given format is non-existent
            else:
                abort(404)
        response = jsonify(data)
        return response, 200
    else:
        message = "Content is not yet published."
        return jsonify({
            "id": "{}_{}_".format(collection_id, publication_id),
            "language": language,
            "error": message
        }), 403

def create_bibl_data(metadata, publication_id, language, est_or_ms):
    bibl_data = {
        "id": publication_id,
        "manuscript_id": None,
        "publication_title": None,
        "publication_subtitle": None,
        "published_by": None,
        "document_type": None,
        "original_language": None,
        "orig_lang_abbr": [],
        "publication_date": None,
        "publication_archive_info": None,
        "author": [],
        "sender": [],
        "recipient": [],
        "translations": []
    }
    # keep track of these, so that the same value isn't added twice
    translation_languages = set()
    authors = set()
    senders = set()
    recipients = set()
    translators = set()
    for row in metadata:
        manuscript_id = row.get("manuscript_id")
        if manuscript_id is not None and bibl_data["manuscript_id"] is None:
            bibl_data["manuscript_id"] = manuscript_id
        publication_title = row.get("publication_title")
        if publication_title is not None and bibl_data["publication_title"] is None:
            bibl_data["publication_title"] = publication_title
        publication_subtitle = row.get("publication_subtitle")
        if publication_subtitle is not None and bibl_data["publication_subtitle"] is None:
            bibl_data["publication_subtitle"] = publication_subtitle
        published_by = row.get("published_by")
        if published_by is not None and bibl_data["published_by"] is None:
            bibl_data["published_by"] = published_by
        document_type = row.get("document_type")
        if document_type is not None and bibl_data["document_type"] is None:
            if language == "sv":
                bibl_data["document_type"] = document_type
            if language == "fi":
                # the value may contain more than one document type, as a string
                # each value has to be translated since values are in sv in the db
                document_types = document_type.split(", ")
                translated_document_types = []
                for doc_type in document_types:
                    document_types_fi = get_document_types_fi_dict()
                    if doc_type in document_types_fi.keys():
                        translated_document_types.append(document_types_fi[doc_type])
                    else:
                        translated_document_types.append(document_types_fi["XX"])
                bibl_data["document_type"] = ", ".join(translated_document_types)
        original_language = row.get("original_language")
        if original_language is not None and bibl_data["original_language"] is None and bibl_data["orig_lang_abbr"] == []:
            # the value may contain more than one language, as a string
            original_languages = original_language.split(", ")
            unabbreviated_languages = []
            abbreviated_languages = []
            if language == "sv":
                for orig_lang in original_languages:
                    abbreviated_languages.append(orig_lang)
                    languages_sv = get_languages_sv_dict()
                    if orig_lang in languages_sv.keys():
                        unabbreviated_languages.append(languages_sv[orig_lang])
                    else:
                        unabbreviated_languages.append(languages_sv["XX"])
            if language == "fi":
                for orig_lang in original_languages:
                    abbreviated_languages.append(orig_lang)
                    languages_fi = get_languages_fi_dict()
                    if orig_lang in languages_fi.keys():
                        unabbreviated_languages.append(languages_fi[orig_lang])
                    else:
                        unabbreviated_languages.append(languages_fi["XX"])
            bibl_data["original_language"] = ", ".join(unabbreviated_languages)
            bibl_data["orig_lang_abbr"].extend(abbreviated_languages)
        publication_date = row.get("publication_date")
        if publication_date is not None and bibl_data["publication_date"] is None:
            bibl_data["publication_date"] = publication_date
        publication_archive_info = row.get("publication_archive_info")
        if publication_archive_info is not None and bibl_data["publication_archive_info"] is None:
            publication_archive_info = handle_archive_info(publication_archive_info, language)
            bibl_data["publication_archive_info"] = publication_archive_info
        author = row.get("author")
        if author is not None and author not in authors:
            bibl_data["author"].append(author)
            authors.add(author)
        sender = row.get("sender")
        if sender is not None and sender not in senders:
            bibl_data["sender"].append(sender)
            senders.add(sender)
        recipient = row.get("recipient")
        if recipient is not None and recipient not in recipients:
            bibl_data["recipient"].append(recipient)
            recipients.add(recipient)
        if est_or_ms == "est":
            translated_into = row.get("translated_into")
            if translated_into is not None:
                if language == "sv":
                    if translated_into == "sv":
                        unabbreviated_translated_into = "till svenska"
                    if translated_into == "fi":
                        unabbreviated_translated_into = "till finska"
                if language == "fi":
                    if translated_into == "sv":
                        unabbreviated_translated_into = "ruotsiksi"
                    if translated_into == "fi":
                        unabbreviated_translated_into = "suomeksi"
                translator = row.get("translator")
                if translated_into not in translation_languages:
                    translation_data = {
                        "translated_into": unabbreviated_translated_into,
                        "translators": []
                    }
                    bibl_data["translations"].append(translation_data)
                    translation_languages.add(translated_into)
                # find the translation data for the translated language
                for translation in bibl_data["translations"]:
                    if translation["translated_into"] == unabbreviated_translated_into and translator not in translators:
                        translation["translators"].append(translator)
                        translators.add(translator)
                        break
    return bibl_data

# endpoint for the reading text column, "est"
@app.route("/api/<project>/text/<collection_id>/<publication_id>/est-i18n/<language>")
@cross_origin()
def get_est(project, collection_id, publication_id, language):
    published_collections = get_published_collections(project)
    # None means that the given project value was wrong
    if published_collections is None:
        abort(404)
    publication_published_status = queries.get_publication_published_status(collection_id, publication_id)
    # if status is None, then the given combo of collection id 
    # and publication id doesn't exist
    if publication_published_status is None:
        abort(404)
    if published_collections != [] and int(collection_id) in published_collections and (publication_published_status == 1 or publication_published_status == 2):
        file_path = queries.get_est_file_path(publication_id, language)
        if file_path is None:
            data = {
                "id": "{}_{}_est".format(collection_id, publication_id),
                "content": "",
                "language": language
            }
        else:
            content = transform(file_path, language)
            data = {
                "id": "{}_{}_est".format(collection_id, publication_id),
                "content": content,
                "language": language
            }
        response = jsonify(data)
        return response, 200
    else:
        message = "Content is not yet published."
        return jsonify({
            "id": "{}_{}_est".format(collection_id, publication_id),
            "error": message
        }), 403

# endpoint for the facsimile column
@app.route("/api/<project>/facsimiles/<publication_id>")
@cross_origin()
def get_facsimiles(project, publication_id):
    published_collections = get_published_collections(project)
    # None means that the given project value was wrong
    if published_collections is None:
        abort(404)
    if published_collections != []:
        facsimile_data = queries.get_facsimile_data(publication_id, published_collections)
        response = jsonify(facsimile_data)
        return response, 200
    else:
        message = "Content is not yet published."
        return jsonify({
            "error": message
        }), 403

# endpoint for the collections (the page called "content")
@app.route("/api/<project>/collections/<language>")
@cross_origin()
def get_collections(project, language):
    published_collections = get_published_collections(project)
    # None means that the given project value was wrong
    if published_collections is None:
        abort(404)
    if published_collections != []:
        collections_data = queries.get_collections_data(project, language, published_collections)
        response = jsonify(collections_data)
        return response, 200
    else:
        message = "Content is not yet published."
        return jsonify({
            "error": message
        }), 403

# endpoint for the metadata column
@app.route("/api/<project>/publications/<publication_id>/metadata/<language>")
@cross_origin()
def get_metadata(project, publication_id, language):
    published_collections = get_published_collections(project)
    # None means that the given project value was wrong
    if published_collections is None:
        abort(404)
    if published_collections != []:
        metadata = queries.get_publication_metadata(publication_id, language, published_collections)
        if metadata != []:
            alternative_facsimiles = queries.get_alternative_facsimiles(publication_id)
            if alternative_facsimiles == []:
                alternative_facsimiles = None
            # there can be several authors, senders, recipients, translations,
            # translators and facsimiles for a publication, but only one value
            # for the other keys
            data = {
                "id": publication_id,
                "manuscript_id": None,
                "publication_title": None,
                "publication_subtitle": None,
                "published_by": None,
                "document_type": None,
                "original_language": None,
                "publication_date": None,
                "author": [],
                "sender": [],
                "recipient": [],
                "translations": [],
                "facsimiles": []
            }
            # lists used for sorting the author/sender/recipient-lists,
            # which only contain full names
            # according to the last name of the persons
            author_last_names = []
            sender_last_names = []
            recipient_last_names = []
            # keep track of these, so that the same value isn't added twice
            translation_languages = set()
            authors = set()
            senders = set()
            recipients = set()
            translators = set()
            for row in metadata:
                manuscript_id = row.get("manuscript_id")
                if manuscript_id is not None and data["manuscript_id"] is None:
                    data["manuscript_id"] = manuscript_id
                publication_title = row.get("publication_title")
                if publication_title is not None and data["publication_title"] is None:
                    data["publication_title"] = publication_title
                publication_subtitle = row.get("publication_subtitle")
                if publication_subtitle is not None and data["publication_subtitle"] is None:
                    data["publication_subtitle"] = publication_subtitle
                published_by = row.get("published_by")
                if published_by is not None and data["published_by"] is None:
                    data["published_by"] = published_by
                document_type = row.get("document_type")
                if document_type is not None and data["document_type"] is None:
                    if language == "sv":
                        data["document_type"] = document_type
                    if language == "fi":
                        # the value may contain more than one document type, as a string
                        # each value has to be translated since values are in sv in the db
                        document_types = document_type.split(", ")
                        translated_document_types = []
                        for doc_type in document_types:
                            document_types_fi = get_document_types_fi_dict()
                            if doc_type in document_types_fi.keys():
                                translated_document_types.append(document_types_fi[doc_type])
                            else:
                                translated_document_types.append(document_types_fi["XX"])
                        data["document_type"] = ", ".join(translated_document_types)
                original_language = row.get("original_language")
                if original_language is not None and data["original_language"] is None:
                    # the value may contain more than one language, as a string
                    original_languages = original_language.split(", ")
                    unabbreviated_languages = []
                    if language == "sv":
                        for orig_lang in original_languages:
                            languages_sv = get_languages_sv_dict()
                            if orig_lang in languages_sv.keys():
                                unabbreviated_languages.append(languages_sv[orig_lang])
                            else:
                                unabbreviated_languages.append(languages_sv["XX"])
                    if language == "fi":
                        for orig_lang in original_languages:
                            languages_fi = get_languages_fi_dict()
                            if orig_lang in languages_fi.keys():
                                unabbreviated_languages.append(languages_fi[orig_lang])
                            else:
                                unabbreviated_languages.append(languages_fi["XX"])
                    data["original_language"] = ", ".join(unabbreviated_languages)
                publication_date = row.get("publication_date")
                if publication_date is not None and data["publication_date"] is None:
                    data["publication_date"] = publication_date
                author = row.get("author")
                author_last_name = row.get("author_last_name")
                if author is not None and author not in authors:
                    data["author"].append(author)
                    authors.add(author)
                    if author_last_name is None:
                        author_last_name = ""
                    author_last_names.append(author_last_name)
                sender = row.get("sender")
                sender_last_name = row.get("sender_last_name")
                if sender is not None and sender not in senders:
                    data["sender"].append(sender)
                    senders.add(sender)
                    if sender_last_name is None:
                        sender_last_name = ""
                    sender_last_names.append(sender_last_name)
                recipient = row.get("recipient")
                recipient_last_name = row.get("recipient_last_name")
                if recipient is not None and recipient not in recipients:
                    data["recipient"].append(recipient)
                    recipients.add(recipient)
                    if recipient_last_name is None:
                        recipient_last_name = ""
                    recipient_last_names.append(recipient_last_name)
                translated_into = row.get("translated_into")
                if translated_into is not None:
                    if language == "sv":
                        if translated_into == "sv":
                            unabbreviated_translated_into = "till svenska"
                        if translated_into == "fi":
                            unabbreviated_translated_into = "till finska"
                    if language == "fi":
                        if translated_into == "sv":
                            unabbreviated_translated_into = "ruotsiksi"
                        if translated_into == "fi":
                            unabbreviated_translated_into = "suomeksi"
                    translator = row.get("translator")
                    if translated_into not in translation_languages:
                        translation_data = {
                            "translated_into": unabbreviated_translated_into,
                            "translators": []
                        }
                        data["translations"].append(translation_data)
                        translation_languages.add(translated_into)
                    # find the translation data for the translated language
                    for translation in data["translations"]:
                        if translation["translated_into"] == unabbreviated_translated_into and translator not in translators:
                            translation["translators"].append(translator)
                            translators.add(translator)
                            break
                # the metadata query only fetched the main facsimile,
                # so there's just one facsimile to add here
                # only add it once
                # since this is the main facsimile, its priority value is always 1
                if data["facsimiles"] == []:
                    archive_info = row.get("archive_info")
                    facs_coll_id = row.get("facs_coll_id")
                    if archive_info is not None and facs_coll_id is not None:
                        archive_info = handle_archive_info(archive_info, language)
                        facsimile_data = {
                            "facs_coll_id": facs_coll_id,
                            "priority": 1,
                            "facsimile_title": row["publication_title"],
                            "archive_info": archive_info,
                            "number_of_images": row["number_of_images"],
                            "image_number_info": row["image_number_info"],
                            "external_url": row["external_url"]
                        }
                        data["facsimiles"].append(facsimile_data)
                    elif archive_info is None and facs_coll_id is not None:
                        facsimile_data = {
                            "facs_coll_id": facs_coll_id,
                            "priority": 1,
                            "facsimile_title": row["publication_title"],
                            "archive_info": None,
                            "number_of_images": row["number_of_images"],
                            "image_number_info": row["image_number_info"],
                            "external_url": row["external_url"]
                        }
                        data["facsimiles"].append(facsimile_data)
            # sort authors/senders/recipients according to their last names,
            # even though these lists only contain the full names
            # the persons will be displayed by the frontend in the order of
            # these lists, so sorting makes the result neater
            lists_to_sort = ["author", "sender", "recipient"]
            last_names_lists = [author_last_names, sender_last_names, recipient_last_names]
            for index, list_name in enumerate(lists_to_sort):
                full_names = data.get(list_name, [])
                if len(full_names) > 1 and index < len(last_names_lists):
                    last_names = last_names_lists[index]
                    combined_names = list(zip(full_names, last_names))
                    sorted_names = [name[0] for name in sorted(combined_names, key=lambda x: x[1])]
                    data[list_name] = sorted_names
            # if this publication has more facsimiles than just the main facsimile
            # they get added here
            if alternative_facsimiles is not None:
                for facsimile in alternative_facsimiles:
                    archive_info = facsimile.get("archive_info")
                    facs_coll_id = facsimile.get("facs_coll_id")
                    if archive_info is not None and facs_coll_id is not None:
                        archive_info = handle_archive_info(archive_info, language)
                        facsimile_data = {
                            "facs_coll_id": facs_coll_id,
                            "priority": facsimile["priority"],
                            "facsimile_title": facsimile["facsimile_title"],
                            "archive_info": archive_info,
                            "number_of_images": facsimile["number_of_images"],
                            "image_number_info": facsimile["image_number_info"],
                            "external_url": facsimile["external_url"]
                        }
                        data["facsimiles"].append(facsimile_data)
                    elif archive_info is None and facs_coll_id is not None:
                        facsimile_data = {
                            "facs_coll_id": facs_coll_id,
                            "priority": facsimile["priority"],
                            "facsimile_title": facsimile["facsimile_title"],
                            "archive_info": None,
                            "number_of_images": facsimile["number_of_images"],
                            "image_number_info": facsimile["image_number_info"],
                            "external_url": facsimile["external_url"]
                        }
                        data["facsimiles"].append(facsimile_data)
                # the facsimiles will be displayed by the frontend
                # in the order of this list, so let's sort them according to
                # their priority value
                # if there's just the main facsimile, there's nothing to sort
                data["facsimiles"] = sorted(data["facsimiles"], key=lambda x: x["priority"])
    if published_collections != [] and metadata != []:
        response = jsonify(data)
        return response, 200
    else:
        message = "Content is not yet published."
        return jsonify({
            "error": message
        }), 403

# do some replacements of archive info
# db might have only a general value, but we need language specific values
def handle_archive_info(archive_info, language):
    archive_list = []
    archive_info_split = archive_info.split("; ")
    for archive in archive_info_split:
        if "LM/KA" in archive or "RM/KA" in archive or "AT/KA" in archive:
            if language == "sv":
                archive = archive.replace("LM/KA", "(Leo Mechelins arkiv, Riksarkivet, Helsingfors)")
                archive = archive.replace("RM/KA", "(Robert Montgomerys arkiv, Riksarkivet, Helsingfors)")
                archive = archive.replace("AT/KA", "(Adolf Törngrens arkiv, Riksarkivet, Helsingfors)")
            if language == "fi":
                archive = archive.replace("LM/KA", "(Leo Mechelinin arkisto, Kansallisarkisto, Helsinki)")
                archive = archive.replace("RM/KA", "(Robert Montgomeryn arkisto, Kansallisarkisto, Helsinki)")
                archive = archive.replace("AT/KA", "(Adolf Törngrenin arkisto, Kansallisarkisto, Helsinki)")
        elif ".KA" in archive:
            if language == "sv":
                archive += (" (Leo Mechelins arkiv, Riksarkivet, Helsingfors)")
            if language == "fi":
                archive += (" (Leo Mechelinin arkisto, Kansallisarkisto, Helsinki)")
        elif archive == "KK":
            if language == "sv":
                archive = "Nationalbiblioteket, Helsingfors"
            if language == "fi":
                archive = "Kansalliskirjasto, Helsinki"
        elif archive == "Varastokirjasto":
            if language == "sv":
                archive = "Depåbiblioteket, Kuopio"
            if language == "fi":
                archive = "Varastokirjasto, Kuopio"
        elif archive.endswith("HKA"):
            if language == "sv":
                archive = archive.replace("HKA", "(Helsingfors stadsarkiv, Helsingfors)")
            if language == "fi":
                archive = archive.replace("HKA", "(Helsingin kaupunginarkisto, Helsinki)")
        archive_list.append(archive)
    archive_info = "; ".join(archive_list)
    return archive_info

# endpoint for person info (shown as tooltip/pop-up in the texts)
@app.route("/api/<project>/subject/<subject_id>/<language>")
@cross_origin()
def get_subject(project, subject_id, language):
    # the given project value has to be right
    if project != "leomechelin":
        abort(404)
    subject_data = queries.get_subject_data(project, subject_id, language)
    if subject_data is None:
        result = {}
    else:
        result = []
        data_result = contruct_person_data(subject_data, language, result)
        result = dict(data_result[0])
    response = jsonify(result)
    return response, 200

# endpoint for the index of persons
@app.route("/api/<project>/persons/<language>")
@cross_origin()
def get_persons(project, language):
    # the given project value has to be right
    if project != "leomechelin":
        abort(404)
    persons = queries.get_persons_data(project, language)
    result = []
    for person in persons:
        try:
            result = contruct_person_data(person, language, result)
        except:
            continue
    # the endpoint provides the whole person index at once
    # already sorted alphabetically
    result.sort(key=lambda x: x["sort_by"])
    response = jsonify(result)
    return response, 200

def contruct_person_data(person, language, result):
    id = person[0]
    first_name = person[1]
    last_name = person[2]
    preposition = person[3]
    full_name = person[4]
    description = person[5]
    date_born = person[6]
    date_deceased = person[7]
    alias = person[8]
    previous_last_name = person[9]
    data = {}
    data["id"] = id
    data["first_name"] = first_name
    data["last_name"] = last_name
    data["preposition"] = preposition
    data["full_name"] = full_name
    data["description"] = description
    if date_born == "XXXX-XX-XX":
        date_born = None
    data["date_born"] = date_born
    if date_deceased == "XXXX-XX-XX":
        date_deceased = None
    data["date_deceased"] = date_deceased
    if alias is not None:
        data["alias"] = "även kallad " + alias
    else:
        data["alias"] = alias
    data["previous_last_name"] = previous_last_name
    if language == "sv":
        if preposition is not None and last_name is not None and first_name is not None:
            data["name_for_list"] = preposition + " " + last_name + ", " + first_name
        elif preposition is None and last_name is not None and first_name is not None:
            data["name_for_list"] = last_name + ", " + first_name
        elif preposition is not None and last_name is not None and first_name is None:
            data["name_for_list"] = preposition + " " + last_name
        elif preposition is None and last_name is not None and first_name is None:
            data["name_for_list"] = last_name
        else:
            data["name_for_list"] = first_name
    if language == "fi":
        if preposition is not None and last_name is not None and first_name is not None:
            data["name_for_list"] = last_name + ", " + first_name + " " + preposition 
        elif preposition is None and last_name is not None and first_name is not None:
            data["name_for_list"] = last_name + ", " + first_name
        elif preposition is not None and last_name is not None and first_name is None:
            data["name_for_list"] = last_name + ", " + preposition
        elif preposition is None and last_name is not None and first_name is None:
            data["name_for_list"] = last_name
        else:
            data["name_for_list"] = first_name
    if last_name is not None and first_name is not None:
        data["sort_by"] = last_name + " " + first_name
    elif last_name is not None and first_name is None:
        data["sort_by"] = last_name
    else:
        data["sort_by"] = first_name
    dates = [date_born, date_deceased]
    i = 0
    for date in dates:
        if date is not None and date != "XXXX-XX-XX":
            split_date = date.split("-")
            year = split_date[0]
            month = split_date[1] if len(split_date) > 1 else "XX"
            day = split_date[2] if len(split_date) > 2 else "XX"
            if month.startswith("0"):
                month = month.replace("0", "", 1)
            if day.startswith("0"):
                day = day.replace("0", "", 1)
            if year == "XXXX" and (day != "XX" or month != "XX"):
                year = "?"
            if day == "XX" and month != "XX":
                day = "?"
            if month == "XX" and day != "XX":
                month = "?"
            if i == 0:
                lived_between_start = day + "." + month + "." + year
            else:
                lived_between_end = day + "." + month + "." + year
        else:
            if i == 0:
                lived_between_start = ""
            else:
                lived_between_end = ""
        i += 1
    if lived_between_start != "" and lived_between_end != "":
        lived_between = lived_between_start + "–" + lived_between_end
        lived_between = lived_between.replace("XX.XX.", "")
    elif lived_between_start != "" and lived_between_end == "":
        if language == "sv":
            lived_between = "f. " + lived_between_start
        if language == "fi":
            lived_between = "s. " + lived_between_start
        lived_between = lived_between.replace("XX.XX.", "")
    elif lived_between_start == "" and lived_between_end != "":
        if language == "sv":
            lived_between = "d. " + lived_between_end
        if language == "fi":
            lived_between = "k. " + lived_between_end
        lived_between = lived_between.replace("XX.XX.", "")
    else:
        lived_between = None
    data["lived_between"] = lived_between
    result.append(data)
    return result

# endpoint for the introduction text
@app.route("/api/<project>/text/<collection_id>/<publication_id>/inl/<language>")
@cross_origin()
def get_introduction(project, collection_id, publication_id, language):
    # checking the published status for the collection is enough
    # since publication id is irrelevant in the case of introductions
    published_collections = get_published_collections(project)
    # None means that the given project value was wrong
    if published_collections is None:
        abort(404)
    if published_collections != [] and int(collection_id) in published_collections:
        file_path = queries.get_intro_file_path(collection_id, language)
        content = transform(file_path, language)
        data = {
            "id": "{}_{}_inl".format(collection_id, publication_id),
            "language": language,
            "content": content
        }
        response = jsonify(data)
        return response, 200
    else:
        message = "Content is not yet published."
        return jsonify({
            "id": "{}_{}_inl".format(collection_id, publication_id),
            "language": language,
            "error": message
        }), 403

# endpoint for the title page
@app.route("/api/<project>/text/<collection_id>/<publication_id>/tit/<language>")
@cross_origin()
def get_title(project, collection_id, publication_id, language):
    # checking the published status for the collection is enough
    # since publication id is irrelevant in the case of title pages
    published_collections = get_published_collections(project)
    # None means that the given project value was wrong
    if published_collections is None:
        abort(404)
    if published_collections != [] and int(collection_id) in published_collections:
        file_path = queries.get_title_file_path(collection_id, language)
        content = transform(file_path, language)
        data = {
            "id": "{}_{}_tit".format(collection_id, publication_id),
            "language": language,
            "content": content
        }
        response = jsonify(data)
        return response, 200
    else:
        message = "Content is not yet published."
        return jsonify({
            "id": "{}_{}_tit".format(collection_id, publication_id),
            "language": language,
            "error": message
        }), 403

# endpoint for the reference text and possible urn/permanent identifier
@app.route("/api/<project>/urn/<url>/")
@cross_origin()
def get_urn_and_reference(project, url):
    # the given project value has to be right
    if project != "leomechelin":
        abort(404)
    url = unquote(unquote(url))
    urn_and_reference_data = queries.get_urn_data(url)
    if urn_and_reference_data is None or urn_and_reference_data == []:
        empty_data = []
        response = jsonify(empty_data)
    else:    
        response = jsonify({**dict(urn_and_reference_data)})
    return response, 200

# endpoint for the text download modal
@app.route("/api/<project>/collection/<collection_id>/i18n/<language>")
@cross_origin()
def get_collection(project, collection_id, language):
    published_collections = get_published_collections(project)
    # None means that the given project value was wrong
    if published_collections is None:
        abort(404)
    if published_collections != [] and int(collection_id) in published_collections:
        collection_data = queries.get_collection_data(collection_id, language)
        response = [dict(collection_data)]
        return jsonify(response), 200
    else:
        message = "Content is not yet published."
        response_data = {
            "error": message
        }
        return jsonify([response_data]), 403

# endpoint for all publications of a collection
@app.route("/api/<project>/collection/<collection_id>/publications/<language>")
@cross_origin()
def get_publications_for_collection(project, collection_id, language):
    published_collections = get_published_collections(project)
    # None means that the given project value was wrong
    if published_collections is None:
        abort(404)
    if published_collections != [] and int(collection_id) in published_collections:
        publications_data = queries.get_publications_data(collection_id, language)
        publication_data = {
            "publication_id": None,
            "publication_group_id": None,
            "publication_title": None,
            "publication_subtitle": None,
            "published_by": None,
            "document_type": None,
            "original_language": None,
            "publication_date": None,
            "archive_info": None
        }
        for publication in publications_data:
            publication_id = publication.get("publication_id")
            publication_data["publication_id"] = publication_id
            publication_title = publication.get("publication_title")
            if publication_title is not None:
                publication_data["publication_title"] = publication_title
            publication_subtitle = publication.get("publication_subtitle")
            if publication_subtitle is not None:
                publication_data["publication_subtitle"] = publication_subtitle
            published_by = publication.get("published_by")
            if published_by is not None:
                publication_data["published_by"] = published_by
            document_type = publication.get("document_type")
            if document_type is not None:
                if language == "sv":
                    publication_data["document_type"] = document_type
                if language == "fi":
                    # the value may contain more than one document type, as a string
                    # each value has to be translated since values are in sv in the db
                    document_types = document_type.split(", ")
                    translated_document_types = []
                    for doc_type in document_types:
                        document_types_fi = get_document_types_fi_dict()
                        if doc_type in document_types_fi.keys():
                            translated_document_types.append(document_types_fi[doc_type])
                        else:
                            translated_document_types.append(document_types_fi["XX"])
                    publication_data["document_type"] = ", ".join(translated_document_types)
            original_language = publication.get("original_language")
            if original_language is not None:
                publication_data["original_language"] = original_language
            publication_date = publication.get("publication_date")
            if publication_date is not None:
                publication["publication_date"] = publication_date
            archive_info = publication.get("archive_info")
            if archive_info is not None:
                archive_info = handle_archive_info(archive_info, language)
                publication["archive_info"] = archive_info
            response = jsonify(publications_data)
        return response, 200
    else:
        message = "Content is not yet published."
        response_data = {
            "error": message
        }
        return jsonify([response_data]), 403

# endpoint for the download texts feature
# depending on whether the publication has content or not,
# there will be different options on the site 
@app.route("/api/<project>/publication/<publication_id>")
@cross_origin()
def get_publication(project, publication_id):
    # the given project value has to be right
    if project != "leomechelin":
        abort(404)
    # if the publication is deleted, there's nothing to fetch
    no_publication = queries.publication_deleted(publication_id)
    if no_publication[0] == 1:
        abort(404)
    else:
        collection_id = queries.find_out_collection(publication_id)[0]
        published_collections = get_published_collections(project)
        if published_collections != [] and int(collection_id) in published_collections:
            languages = ["sv", "fi"]
            data = {
                "id": publication_id,
                "publication_group_id": None,
                "original_filename": {
                    "sv": "",
                    "fi": ""
                },
                "deleted": 0
            }
            for language in languages:
                publication_data = queries.get_publication_data(publication_id, language)
                if publication_data is not None:
                    publication_group_id = publication_data[0]
                    file = publication_data[1]
                    if data["publication_group_id"] is None:
                        data["publication_group_id"] = publication_group_id
                    content = transform(file, language)
                    if content != "":
                        data["original_filename"][language] = "has_content"
            response = jsonify([data])
            return response, 200
        else:
            message = "Content is not yet published."
            response_data = {
                "error": message
            }
            return jsonify([response_data]), 403

# endpoint for all ms:s for a publication
@app.route("/api/<project>/text/<collection_id>/<publication_id>/list/ms")
@cross_origin()
def get_ms_for_publication(project, collection_id, publication_id):
    published_collections = get_published_collections(project)
    # None means that the given project value was wrong
    if published_collections is None:
        abort(404)
    publication_published_status = queries.get_publication_published_status(collection_id, publication_id)
    no_publication = queries.publication_deleted(publication_id)
    # if status is None, then the given combo of collection id 
    # and publication id doesn't exist
    # and if the publication is deleted, there's nothing to fetch
    if publication_published_status is None or no_publication[0] == 1:
        abort(404)
    if published_collections != [] and int(collection_id) in published_collections and (publication_published_status == 1 or publication_published_status == 2):
        ms_list_data = queries.get_ms_list_data(publication_id)
        # if the publication simply doesn't have an ms
        # and only consists of the reading text
        # or if the ms has been deleted
        empty_data = {
            "id": "{}_{}".format(collection_id, publication_id),
            "manuscripts": []
        }
        if ms_list_data is None:
            data = empty_data
        else:
            pm_id = ms_list_data[0]
            name = ms_list_data[1]
            type = ms_list_data[2]
            archive_info = ms_list_data[3]
            language = ms_list_data[4]
            file = ms_list_data[5]
            data = {
                "id": "{}_{}".format(collection_id, publication_id),
                "manuscripts": [{
                    "id": pm_id,
                    "name": name,
                    "language": language,
                    "type": type,
                    "archive_info": archive_info,
                    "original_filename": "",
                }]
            }
            content = transform_ms(file, language)
            if content != "":
                data["manuscripts"][0]["original_filename"] = "has_content"
            # if there's no text content, this equals a non-existent ms
            else:
                data = empty_data
        response = jsonify(data)
        return response, 200
    else:
        message = "Content is not yet published."
        return jsonify({
            "id": "{}_{}_".format(collection_id, publication_id),
            "error": message
        }), 403

# endpoint for the table of contents
@app.route("/api/<project>/toc/<collection_id>/<language>")
@cross_origin()
def handle_toc_lang(project, collection_id, language):
    published_collections = get_published_collections(project)
    # None means that the given project value was wrong
    if published_collections is None:
        abort(404)
    if published_collections != [] and int(collection_id) in published_collections:
        SOURCE_FOLDER = '.'
        file_path = safe_join(SOURCE_FOLDER, "toc", f"{collection_id}_{language}.json")
        try:
            with open (file_path, "r", encoding="utf-8-sig") as source_file:
                contents = source_file.read()
                return contents, 200
        except Exception:
            abort(404)
    else:
        message = "Content is not yet published."
        return jsonify({
            "id": "{}_{}".format(collection_id, language),
            "error": message
        }), 403

# the endpoints for metadata and downloadable text
# provide translated values 
def get_languages_fi_dict():
    languages_fi = {
        "fi": "suomi",
        "sv": "ruotsi",
        "en": "englanti",
        "es": "espanja",
        "fr": "ranska",
        "de": "saksa",
        "it": "italia",
        "no": "norja",
        "ru": "venäjä",
        "la": "latina",
        "da": "tanska",
        "XX": "määrittelemätön"
    }
    return languages_fi

# the endpoints for metadata and downloadable text
# provide translated values 
def get_languages_sv_dict():
    languages_sv = {
        "fi": "finska",
        "sv": "svenska",
        "en": "engelska",
        "es": "spanska",
        "fr": "franska",
        "de": "tyska",
        "it": "italienska",
        "no": "norska",
        "ru": "ryska",
        "la": "latin",
        "da": "danska",
        "XX": "okänt"
    }
    return languages_sv

# the endpoints for metadata and downloadable text
# provide translated values    
def get_document_types_fi_dict():
    document_types_fi = {
        "adress": "adressi",
        "almanacka": "almanakka",
        "artikel": "lehtikirjoitus",
        "biographica": "biographica",
        "diplom": "kunniakirja",
        "dokument": "asiakirja",
        "föreläsning": "luento",
        "lantdagsprotokoll": "valtiopäivien pöytäkirja",
        "lyrik": "runo",
        "inbjudan": "kutsu",
        "mottaget brev": "LM:n vastaanottama kirje",
        "mottaget telegram": "LM:n vastaanottama sähke",
        "opera": "ooppera",
        "PM": "muistio",
        "program": "ohjelma",
        "protokoll": "pöytäkirja",
        "publikation": "julkaisu",
        "stadsfullmäktiges protokoll": "kaupunginvaltuuston pöytäkirja",
        "studierelaterat": "opinnot",
        "sänt brev": "LM:n lähettämä kirje",
        "sänt telegram": "LM:n lähettämä sähke",
        "tal": "puhe",
        "teater": "teatteri",
        "tidningsurklipp": "lehtileike",
        "tillfällesdikt": "tilanneruno",
        "verk": "teos",
        "visitkort": "käyntikortti",
        "XX": "määrittelemätön dokumenttityyppi"
    }
    return document_types_fi

if __name__ == '__main__':
    app.run(host='', port=5000, debug=True)