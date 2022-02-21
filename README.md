# database_population
Python scripts for populating a database for a digital edition.

The database belongs to an edition project which publishes the works of the Finnish author and politician Leo Mechelin (1839–1914). The edition contains thousands of texts, which will be published on a website and to some extent also as e-books and in print. The main purpose of the project is to make historical texts and archive material accessible online by digitizing, transcribing and translating documents and by presenting them in a meaningful context.

The PostgreSQL database is part of a generic digital edition platform, managed by the Society of Swedish Literature in Finland (see https://github.com/slsfi/digital_edition_documentation/wiki). If you're planning to publish an XML-based online edition, this is an open source project that might be of interest.

The database contains information about editions (i.e. collections of texts), texts, manuscripts, facsimiles (i.e. images of the original documents), editorial texts and persons related to the texts. Contrary to the earlier projects using the same digital edition platform (and thus database), this project is bilingual (Swedish/Finnish), so some changes were made to the original database schema in order to accommodate translations.

These scripts populate the different tables of the database and also create the needed infrastructure for the project's workflow. Each document, e.g. a letter, a newspaper article, a printed book or a poem, has at least two XML files, a Swedish and a Finnish one. If the document was originally written in another language, there is a third file. Every document also has facsimile images, or a link to another site containing the images. The scripts create all the needed XML files and their folder structure and save the file paths in the db. The files are in a GitHub repository. Thus editors can add content to any file, i.e. transcribe or translate any text they like, without having to create any file themselves and without having to update the db with the corresponding file paths. This way file names and folder structures are also kept uniform and typos in them are prevented. Whenever content then is added to a file and committed, it appears on the web site. The scripts also connect, rename and resize all the images for the facsimile view, and create the tables of content for the site (JSON files).

The main achievement of the scripts in this repo is that the db has been populated entirely by them. Some smaller corrections are naturally made continuously in the db, but otherwise everything is added by running the scipts and not by hand. Also, the spreadsheets that contain the original info about the documents were made by others before there was any notion of the db and its structure. Initially, only the file name of the first image for each document was recorded, and senders/receivers of letters were recorded in multiple ways. In short, there was a lot of unstructured data, and I had to find ways of sorting it and extracting the useful bits. I am pleased with how neatly persons, different language versions of a text, images and metadata are now all connected. This enables a great digital edition and a fully functioning workflow where no one has to do unnecessary work.

## 1. Populate table subject

## 1. a) sort_persons.py
The starting point was a large Excel file containing info about documents, including the name of the author of each document. I extracted the names and made them into a csv. The names had been recorded differently, sometimes as "Surname, Forename(s)", and sometimes as "Forename(s) Surname", all name parts in the same field. The same person could also have been recorded several times in different ways. This script gets the names correctly split and ordered so that duplicates and errors can be found. This is the first step towards populating table subject, which holds info about persons.

## 1. b) deal_with_persons.py
This script populates table subject. The starting point was a csv with info about persons, originating from the list constructed by sort_persons.py. If a person has a different or differently spelled name in Finnish, connections are made to tables translation and translation_text. The output includes two dictionaries, needed later when populating table publication.

## 2. Find the images for each document

## 2. a) find_facsimiles_old_signum.py
The starting point is a csv file with info about documents that will be made into texts (i.e. publications) in our edition. An URL has been recorded for each document. The URL contains an archive signum and an image signum/number for the document's first image. We need to find out the (probable) last signum too, so that we can find all images belonging to a text, not just the first one. This script finds out which images belong to which document, and then stores file paths to those images.

## 2. b) find_facsimiles_new_signum.py
This is a slightly different version of the script above. The starting point is a similar csv file with info about the publication and its images. This time both the first and last image signum of each publication's facsimile is in the file, but we need to modify the signums a bit. Now there may also be an alternative facsimile for some publications, which has to be recorded correctly.

## 3. Populate table publication
The following scripts populate table publication, which holds the main info about each text. Each category of texts has its different needs and its own ways of constructing titles and making connections to persons, so there's a different script for each category. The starting point in every case is a csv file containing info about the texts, but these lists may differ quite a lot. The csv was in most cases updated earlier on in the process by one of the find_facsimiles-scripts, and the populate_publication-scripts add more info to the csv: the publication id and title. They will be needed later when populating table facsimile_collection. Each script creates all the needed XML files for the publication (and its manuscript, if needed) and updates the db with those file paths. The scripts also add a template to the XML files, so editors can concentrate on adding the document's text instead of its header stuff.

## 4. a) populate_publication_received_letter.py
This script adds the received letters. It also populates publication_manuscript, translation, translation_text, event, event_connection and event_occurrence in order to make the necessary connections between texts, persons and translations. It makes the date format uniform and constructs the title of each letter according to date and sender, in Swedish and Finnish. It makes some changes to the title before using it as part of the file name, and creates a folder structure that makes it easy for editors to find the right files.

## 4. b) populate_publication_sent_letter.py
This script adds the sent letters. It is very similar to the one above, it just makes the titles and the connections to persons the other way round (as a sent letter obviously is the exact opposite of a received one).

