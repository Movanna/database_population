# database_population
**Python scripts for populating a database for a digital edition.**

The database belongs to an edition project which publishes the works of the Finnish author and politician **Leo Mechelin** (1839–1914). The edition contains thousands of texts, which will be published on a website and to some extent also as e-books and in print. The main purpose of the project is to make historical texts and archive material accessible online by digitizing, transcribing and translating documents and by presenting them in a meaningful context.

The PostgreSQL database is part of a **generic digital edition platform**, managed by the Society of Swedish Literature in Finland (see https://github.com/slsfi/digital_edition_documentation/wiki). If you're planning to publish an XML-based online edition, this is an open source project that might be of interest.

The database contains information about editions (i.e. collections of texts), texts, manuscripts, facsimiles (i.e. images of the original documents), editorial texts and persons related to the texts. Contrary to the earlier projects using the same digital edition platform (and thus database), this project is bilingual (Swedish/Finnish), so some changes were made to the original database schema in order to accommodate translations.

**These scripts populate the different tables of the database and also create the needed infrastructure for the project's workflow.** Each document, e.g. a letter, a newspaper article, a printed book or a poem, has at least two XML files, a Swedish and a Finnish one. If the document was originally written in another language, there is a third file. Every document also has facsimile images, or a link to another site containing the images. The scripts create all the needed XML files and their folder structure and save the file paths in the db. The files are in a GitHub repository. Thus editors can add content to any file, i.e. transcribe or translate any text they like, without having to create any file themselves and without having to update the db with the corresponding file paths. This way file names and folder structures are also kept uniform and typos in them are prevented. Whenever content then is added to a file and committed, it appears on the web site. The scripts also find, connect, rename and resize all the images for the facsimile view, and create the tables of content for the site (JSON files).

**The main achievement of the scripts in this repo** is that the db has been populated entirely by them. Some smaller corrections are naturally made continuously in the db, but otherwise everything is added by running the scipts and not by hand. Also, the spreadsheets that contain the original info about the documents were made by others before there was any notion of the db and its structure. Initially, only the file name of the first image for each document was recorded, and senders/receivers of letters were recorded in multiple ways. In short, there was a lot of unstructured data, and I had to find ways of sorting it and extracting the useful bits. I am pleased with how neatly persons, different language versions of a text, images and metadata are now all connected. This enables a great digital edition and a fully functioning workflow where no one has to do unnecessary work.

**All scripts written by me**, Anna Movall, in 2021–2022, except for two functions in populate_facsimile_collection.py and the whole of fetch_facsimile_metadata.py (which I'm still the co-author of). I thus also **planned the resulting workflow for the project**, because the digital publishing platform holds no solution whatsoever for that, it just provides the general backend and frontend.

## 1. Populate table subject
Table subject holds information about persons.

### 1. a) sort_persons.py
The starting point was a large Excel file containing info about documents, including the name of the author of each document. I extracted the names and made them into a csv. The names had been recorded differently, sometimes as "Surname, Forename(s)", and sometimes as "Forename(s) Surname", all name parts in the same field. The same person could also have been recorded several times in different ways. This script gets the names correctly split and ordered so that duplicates and errors can be found. This is the first step towards populating table subject, which holds info about persons.

### 1. b) deal_with_persons.py
This script populates table subject. The starting point was a csv with info about persons, originating from the list constructed by sort_persons.py. If a person has a different or differently spelled name in Finnish, connections are made to tables translation and translation_text. The output includes two dictionaries, needed later when populating table publication.

## 2. Find the images for each document
Either the first image of a document or the first and last images are recorded, but all images need to be found. Also, there are many hundreds of directories and they have even more subdirectories, and we don't know beforehand where the images are to be found, because the file path is not recorded, just a combination of the directory name and the file name.

### 2. a) find_facsimiles_old_signum.py
The starting point is a csv file with info about documents that will be made into texts (i.e. publications) in our edition. An URL has been recorded for each document. The URL contains an archive signum and an image signum/number for the document's first image. We need to find out the (probable) last signum too, so that we can find all images belonging to a text, not just the first one. This script finds out which images belong to which document, and then stores file paths to those images.

### 2. b) find_facsimiles_new_signum.py
This is a slightly different version of the script above. The starting point is a similar csv file with info about the publication and its images. This time both the first and last image signum of each publication's facsimile is in the file, but we need to modify the signums a bit. Now there may also be an alternative facsimile for some publications, which has to be found and recorded correctly.

## 3. Populate table publication
The following scripts populate table publication, which holds the main info about each text. Each category of texts has its different needs and its own ways of constructing titles and making connections to persons, so there's a different script for each category. The starting point in every case is a csv file containing info about the texts, but these lists may differ quite a lot. The csv was in most cases updated earlier on in the process by one of the find_facsimiles-scripts, and the populate_publication-scripts add more info to the csv: the publication id and title. They will be needed later when populating table facsimile_collection. Each script creates all the needed XML files for the publication (and its manuscript, if needed) and updates the db with those file paths. The scripts also add a template to the XML files, so editors can concentrate on adding the document's text instead of its header stuff.

### 3. a) populate_publication_received_letter.py
This script adds received letters. It also populates publication_manuscript, translation, translation_text, event, event_connection and event_occurrence in order to make the necessary connections between texts, persons and translations. It makes the date format uniform and constructs the title of each letter according to date and sender, in Swedish and Finnish. It makes some changes to the title before using it as part of the file name, and creates a folder structure that makes it easy for editors to find the right files.

### 3. b) populate_publication_sent_letter.py
This script adds sent letters. It is very similar to the one above, it just makes the titles and the connections to persons the other way round (as a sent letter obviously is the exact opposite of a received one).

### 3. c) populate_publication_article.py
This script adds newspaper articles. It's a lot less complex, since other persons than Mechelin himself are not involved and there are no manuscripts.

### 3. d) populate_publication_poem.py
This script adds poems. It makes connections similar to the letter-scripts and handles the fact that some poems are manuscripts and others are printed.

### 3. e) populate_publication_misc.py
This script adds miscellaneous texts, mainly manuscripts. It is very similar to the one above.

### 3. f) populate_publication_hansard.py
This script adds hansards, i.e. protocols from the Diet (national council) or lantdagen/valtiopäivät. It is very similar to the article-adding one.

### 3. g) populate_publication_lecture.py
This script adds lectures. It is similar to the others adding manuscripts, except that it also adds subtitles to the publications.

## 4. Populate table publication_facsimile_collection
Table publication_facsimile_collection holds info about the facsimile units, i.e. all the images that together make up the facsimile for a publication. It is connected to table publication through table publication_facsimile, which also determines the order in which the facsimile units will appear if there are two or more of them for a publication.

### 4. a) populate_facsimile_collection.py
This script creates the facsimile folder for each facsimile and fills it with the right images, which are renamed, resized and put into subdirectories, and populates tables publication_facsimile_collection and publication_facsimile. The facsimile folder is named after the db id. The script needs the csv:s which were originally created by the find_facsimiles-scripts and later enriched by the populate_publication-scripts. The csv:s contain info about publications and their facsimiles.

### 4. b) fetch_facsimile_metadata.py
This script is needed if there are no images, just links to https://digi.kansalliskirjasto.fi, which already has digitized the images and put them online. The script fetches metadata based on URL using API and inserts it into table publication_facsimile_collection. The script also updates table publication_facsimile. This way the facsimile info comes straight from the source.

## 5. Fix things afterwards and tidy up the db
As it happens, things change as you go along, and you realise that you have to add more data or come up with a way of fixing certain issues ...

### 5. a) create_facsimiles.py
This script is used for fixing flawed facsimile units that have already been created and added to the database and the file storage. Sometimes you find out afterwards that there are images missing, or that the images are in the wrong order. This script needs the id of the facsimile and the file paths to the correct images, in the right order, and will then create a new facsimile folder and fill it with the new images, which are renamed, resized and put into subdirectories as required. Then the old folder can be replaced.

### 5. b) update_archive_signum.py
This script updates table publication with more extensive archive signums. Good I had all those csv:s saved! This value was in the csv:s but at the moment when I added the publications I just didn't know it was valuable.

### 5. c) update_title_and_signum.py
This script updates publication titles and archive signums in tables publication_manuscript and publication_facsimile_collection. Yes, the same data is in several places, but it makes the db more human friendly to scroll through when there's a title to the manuscript or facsimile, and not just an id. Besides, that wasn't even my idea. The true title is in translation_text though, and that's where I make manual corrections if it turns out to be wrong. But it's annoying to know that there are misleading titles in other tables, if you just fix them in one, so this script makes everything up-to-date in all tables.

### 5. d) add_publication_group.py
This script finds out the right publication_group for each publication according to its date and then updates table publication. Groups were not settled on when I first started adding publications, so this fixes lacking group id:s. Now it could be incorporated in the populate_publication-scripts.

## 6. Create a table of contents for each part of the edition
After a toc has been added the digital edition is actually usable: it now has texts, manuscripts, facsimiles, metadata and a way of navigating between texts. Now editors can keep refining the content and translators can go to the site and find their source texts.

### 6. a) create_toc.py
This script generates a table of contents JSON file containing all publications belonging to a collection, sorted according to group and then chronologically. It creates both a Swedish and a Finnish toc. The toc files are not edited by hand, just generated again if there has been changes to the db (such as publications added or deleted or changed titles, dates, groups).
