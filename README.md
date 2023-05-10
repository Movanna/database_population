# database_population
**Python scripts for populating a PostgreSQL database for a digital edition, for dealing with humanist data and for creating all the infrastructure for the project's workflow, such as XML files.**

The database belongs to an edition project which publishes the works of the Finnish author and politician **Leo Mechelin** (1839–1914). The edition contains tens of thousands of texts, which will be published on a website and to some extent also as e-books and in print. The main purpose of the project is to make historical texts and archive material accessible online by digitizing, transcribing and translating documents and by presenting them in a meaningful context.

The PostgreSQL database is part of a **generic digital edition platform**, managed by the Society of Swedish Literature in Finland (see https://github.com/slsfi/digital_edition_documentation/wiki). If you're planning to publish an XML-based online edition, this is an open source project that might be of interest.

The database contains information about editions (i.e. collections of texts), texts, manuscripts, facsimiles (i.e. images of the original documents), editorial texts and persons related to the texts. Contrary to the earlier projects using the same digital edition platform (and thus database), this project is bilingual (Swedish/Finnish), so some changes were made to the original database schema in order to accommodate translations. The current schema is in digital_edition_database_schema.sql.

**These scripts populate the different tables of the database and also create the needed infrastructure for the project's workflow.** Each document, e.g. a letter, a newspaper article, a printed book or a poem, has at least two XML files, a Swedish and a Finnish one. If the document was originally written in another language, there is a third file. Every document also has facsimile images, or a link to another site containing the images. The scripts create all the needed XML files and their folder structure and save the file paths in the db. The files are in a GitHub repository. Thus editors can add content to any file, i.e. transcribe or translate any text they like, without having to create any file themselves and without having to update the db with the corresponding file paths. This way file names and folder structures are also kept uniform and typos in them are prevented. Whenever content then is added to a file and committed, it appears on the web site. The scripts also find, connect and rename all the images for the facsimile view, and create the tables of content for the site (JSON files).

**The main achievement of the scripts in this repo** is that the db has been populated entirely by them. Some smaller corrections are naturally made continuously in the db, but otherwise everything is added by running the scripts and not by hand. Also, the spreadsheets that contain the original info about the documents were made by others before there was any notion of the db and its structure. Initially, only (parts of) the file path of the first image for each document had been recorded, so you knew that the document's first page was on e.g. image 7, but there was no notion of what the last image was. The names of senders/receivers of letters were also recorded in multiple ways. In short, there was a lot of unstructured data, and I had to find ways of sorting it and extracting the useful bits. I am pleased with how neatly persons, different language versions of a text, images and metadata are now all connected and files created. This enables a great digital edition and a fully functioning workflow where no one has to do unnecessary work.

I thus **planned the entire digital workflow for the project**, because the digital publishing platform holds no solution whatsoever for that, it just provides the general backend and frontend including the database structure.

For the next step in the process of publishing these texts using the digital edition platform, see my repo transform_texts.

## 1. Populate table subject
Table subject holds information about persons.

### 1. a) sort_persons.py
The starting point was a large Excel file containing info about documents, including the name of the author of each document. I extracted the names and made them into a CSV. The names had been recorded differently, sometimes as "Surname, Forename(s)", and sometimes as "Forename(s) Surname", all name parts in the same field. The same person could also have been recorded several times in different ways. This script gets the names correctly split and ordered so that duplicates and errors can be found. This is the first step towards populating table subject, which holds info about persons.

### 1. b) deal_with_persons.py
This script populates table subject. The starting point was a CSV with info about persons, originating from the list constructed by sort_persons.py. If a person has a different or differently spelled name in Finnish, connections are made to tables translation and translation_text. The output includes two dictionaries, needed later when populating table publication.

## 2. Find the images for each document
Either the first image of a document or the first and last images have been recorded, but all images need to be found. Also, there are several thousands of image directories and subdirectories and about 100 000 images, and we don't know beforehand where the images are to be found, because the file path hasn't been recorded, just a combination of a single directory name and the image file number/name.

### 2. a) find_facsimiles_old_signum.py
The starting point is a CSV file with info about documents that will be made into texts (i.e. publications) in our edition. An URL has been recorded for each document. The URL contains an archive signum and an image signum/number for the document's first image. We need to find out the (probable) last signum too, so that we can find all images belonging to a text, not just the first one. This script finds out which images belong to which document, and then stores file paths to those images.

### 2. b) find_facsimiles_new_signum.py
This is a slightly different version of the script above. The starting point is a similar CSV file with info about the publication and its images. This time both the first and last image signum of each publication's facsimile is in the file, but we need to modify the signums a bit. Now there may also be an alternative facsimile for some publications, which has to be found and recorded correctly.

## 3. Populate table publication and create the XML files
The following scripts populate table publication, which holds the main info about each text. Each category of texts has its different needs and its own ways of constructing titles/file paths and making connections to persons, so there's a different script for each category. The starting point in every case is a CSV file containing info about the texts, but these lists may differ quite a lot. The CSV was in most cases updated earlier on in the process by one of the find_facsimiles-scripts, and the populate_publication-scripts add more info to the CSV: the publication ID and title. They will be needed later when populating table facsimile_collection. Each script creates all the needed XML files for the publication (and its manuscript, if needed) and updates the db with those file paths. For some text categorys, such as letters, the scripts also construct the titles for the texts. The scripts also add a template to each XML file, enabling editors to concentrate on adding the document's text instead of its header stuff.

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

## 4. Populate table publication_facsimile_collection and create the image files
Table publication_facsimile_collection holds info about the facsimile units, i.e. all the images that together make up the facsimile for a publication. It is connected to table publication through table publication_facsimile, which also determines the order in which the facsimile units will appear if there are two or more of them for a publication. Script a also creates the needed images and folders, while script b fetches metadata from another source and connects the publication with a link to that site holding the images.

### 4. a) populate_facsimile_collection.py
This script creates the facsimile folder for each facsimile and fills it with the right images, which are renamed and put into a subdirectory. It populates tables publication_facsimile_collection and publication_facsimile. The facsimile folder is named after the db ID. The script needs the CSV:s which were originally created by the find_facsimiles-scripts and later enriched by the populate_publication-scripts. The CSV:s contain info about publications and their facsimiles.

### 4. b) fetch_facsimile_metadata.py
This script is needed if there are no images, just links to https://digi.kansalliskirjasto.fi, which already has digitized the images (mainly newspapers) and published them online. The script fetches metadata based on URL using API and inserts it into table publication_facsimile_collection. The script also updates table publication_facsimile. This way the facsimile info comes straight from the source and the editor only needs to record the URL for the image, not the title, number and date of the newspaper, since this data is fetched by the script.

## 5. Fix things afterwards and tidy up the db
As it happens, things change as you go along, and you realise that you have to add more data or come up with a way of fixing certain issues ...

### 5. a) create_facsimiles.py
This script is used for fixing flawed facsimile units that have already been created and added to the database and the file storage. Sometimes you find out afterwards that there are images missing, or that the images are in the wrong order. This script needs the ID of the facsimile and the file paths to the correct images, in the right order, and will then create a new facsimile folder and fill it with the new images, which are renamed and put into a subdirectory as required. Then the old folder can be replaced.

### 5. b) update_archive_signum.py
This script updates table publication with more extensive archive signums. Good I had all those CSV:s saved! This value was in the CSV:s but at the moment when I added the publications I just didn't know it was valuable.

### 5. c) update_title_and_signum.py
This script updates publication titles and archive signums in tables publication_manuscript and publication_facsimile_collection. Yes, the same data is in several places, but it makes the db more human friendly to scroll through when there's a title to the manuscript or facsimile, and not just an ID. Besides, that wasn't even my idea, the db came like this. The ”true” title is in translation_text though, and that's where I make manual corrections to titles. But it's annoying to know that there are misleading titles in other tables, if you just fix them in one, so this script makes everything neat and up-to-date in all tables.

### 5. d) add_publication_group.py
This script finds out the right publication_group for each publication according to its date and then updates table publication. Groups were not settled on when I first started adding publications, so this fixes lacking group ID:s.

### 5. e) add_translation_for_groups.py
As seen above, groups were a later addition, and translations didn't exist in the beginning. This script adds the translations of the titles of collections and groups by updating tables translation, translation_text, publication_collection and publication_group. Not complicated as such, but I got to use the psycopg2.sql module in order to generate SQL dynamically, because I needed to merge table names to the query. That can't be done by using %s placeholders, since Psycopg will then try quoting the table name as a string value, generating invalid SQL. I hadn't done that before, so that was useful!

### 5. f) add_translator.py
The project realised that the translator of each text should be registered in the database so that his or her name could be displayed together with the other metadata of the text. I created a new table, contribution, and then this script for adding the connection between a specific language version of a text and its translator. The names are kept in table contributor, which already existed. Contributor was probably meant to hold the information I now placed in contribution, but not changing that would have meant repeating the translator's name for each tuple, which seemed unefficient, considering that there will be several thousands of tuples. The script splits names, fetches data and checks if the connection already exists, before populating the table.

### 5. g) delete_or_rename_files.py
When running any of the scripts that populate table publication, the XML files for each entry are created simultaneously. But as it happened, I tested the script on my test database, and then forgot to delete the newly created folders and files as I ran the same script again on the production db. This meant that I ended up with a double set of files: half of them had file names containing id:s from the test db, and half of them had the id:s from the production db that they should actually have. The names of all the different folders and subfolders don't contain id:s, though, and thus they didn't change between the runs, meaning that I couldn't delete the unwanted files without opening each and every subfolder. The db data was fine so it seemed a pity to start deleting it or using a db backup in order to run the populating script again. Hence this script which simply deleted the unwanted files and cleaned up my own mess.

Later on, I had the need to rename lots of files and folders, because it turned out that some senders and receivers of letters had been registered wrong: their names were actually something else. The name of the sender or receiver is included in the file and folder names, and a person may have hundreds of folders and files. So I modified this script into also renaming files and folders if a certain component was present in them.

## 6. Create a table of contents for each part of the edition
After a table of contents has been added to the website the digital edition is actually usable: it now has texts, manuscripts, facsimiles, metadata and a way of navigating between texts. The toc files are not edited by hand, just generated again if there has been changes to the db (such as publications added or deleted or changed titles/dates/groups).

### 6. a) create_toc.py
This script generates a table of contents JSON file out of data in the db. The toc contains all publications belonging to a collection, sorted according to group and then chronologically. If there's a subtitle or some explanatory description of the text, it is added too. The script creates both a Swedish and a Finnish toc, since the web site is bilingual. 

### 6. a) create_new_toc.py
This script replaces the previous one since the new website has more features. The script still generates a table of contents JSON file, which is the side menu of the site. There is a Swedish and a Finnish toc, and they contain all publications belonging to a collection sorted as follows: firstly according to the publications' group id and then chronologically within the group. The toc displays the publication's title and possible descriptions, and on the website it can be sorted according to genre and date. The script fetches publication data from the db and also checks all the files belonging to each publication in order to determine whether this publication has text content or not. In this project, a publication consists either of images and metadata, or of text, metadata and (usually) images. The two cases are styled differently in the side menu depending on their content value.
