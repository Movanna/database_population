# The publishing process for the digital archive Leo Mechelin

These are instructions and documentation written in February–April 2024, after I left the project. The documentation describes the publishing process for this project and is meant to serve as a guideline for anyone continuing the work. It may also be of some use for anyone starting up a new publishing project using the Generic Digital Edition Platform. Its main take-away should, however, be how not to record data, since both these instructions and my work would have been so much easier if the original data had been recorded differently.  

## General

### The spreadsheet
The master data for most of the digital archive's content comes from a spreadsheet in Google Sheets. This file existed long before there was any notion of the database and its structure and before I started working for the project. E.g., almost all of the 10 000 received letters and several other archive units had already been registered. In total there were 20 000 rows containing various amounts of information, and I decided it was better to adapt to the existing spreadsheet rather than spending months on redoing all of the earlier registration. That's why we're stuck with this system and its partially inadequate data.  

The spreadsheet has a rudimentary chronological order, maintained by hand, since it can't be sorted according to date. In fact, the only useful values for sorting are genre and archive unit. They're not perfect either, but at least they produce a somewhat working result. The other fields are basically unsortable:  

**Dates** have been registered in many different and inconsistent ways: "1900-tal", "1882? (1884?)", "7.?.1885", "10.8.1894\[96?\]", "14/27.11.1907", "ca 23.4.1913" and so on. The field containing the **title** of the document may also simply contain the sender or recipient of a letter. **Senders/recipients** have been registered by name and not with an ID, each person usually registered in many different ways: "Sergej Witte", "Witte", "Witte, Sergei", "Witte, Sergei Juljevitsch" and "S. Witte" all refer to the same person. Originally, there was no way of registering the **author** of a text, or even whether Mechelin himself was the author or not. Any field usually contains different data crammed together. Or the field contains mainly one type of data, such as archive unit, but may also have other values, such as a book title or the name of a newspaper. There's no data validation, so there are typos in all categories. There are also many rows containing general info ("Mechelin graduated"/"Mechelin moved to Sweden") which has nothing to do with a specific document.  

Initially, **facsimiles** were registered in the spreadsheet by a single URL, which led to the first image of the document in the National Archives' digital archive. Out of this URL it's possible to construct the file path to the corresponding image on the project's network disk. However, since the document's last image wasn't registered in the spreadsheet, the last image for most of these documents is a qualified guess based on the next document's first image (within the same archive unit, i.e. image folder on the disk). A value for the number of pages in the document has sometimes been registered, but it doesn't correspond to the number of images: the unconsistent digitization process has left us with anything between 1 to 5 pages in the same image, and these pages don't even necessarily belong to the same document. Also, the URLs as such went dead a long time ago. But the facsimile scripts actually handle these issues quite ok.   

If the document's images have been registered after the introduction of the database, there are two values: the first and the last page. If the document's images are in order, that is. If not, then there are a lot of values, which may be read either as all from-values in one cell and all to-values in another cell ("1, 7, 9" and "3, -, 10"), or simply as all values in one cell ("1-3, 7, 9-10"). These cases have to be sorted out by hand, while the simple cases are handled by the scripts. Also, there may be more than one facimile for a single document, if there are several versions of it. Again, the simple cases are handled (semi)automatically and the complicated ones are not.  

The spreadsheet is in active use, meaning that new archive units are still being added as the registration of their documents and images proceeds.  

### The scripts
Everything that goes into the database is primarily added through scripts, unless we're talking about smaller corrections. There are two GitHub repos for the scripts: [database_population](https://github.com/Movanna/database_population) and [transform_texts](https://github.com/Movanna/transform_texts). Their READMEs are quite extensive, and the scripts contain lots of comments.    

Feel free to clone these repos and start your own development. No need to worry about merging; I'm going to freeze my repos as they are, not developing them any further. They'll serve as my portfolio for what I did and how far I got in this project.  

Please observe that the scripts in my public repos differ slightly from the ones I actually used. And the public repos don't contain other files needed in the publishing process, such as certain JSON, CSV and TXT files: they are in the project's private repo. Also make sure to not disclose any sensitive information if you're opting for a public repo for your own development purposes.  

### The database
The database for the project is a PostgreSQL database in Google Cloud, Cloud SQL. There's a production db and a test db.

### The XML and Markdown files
The project's XML and Markdown files are in the project's private repo.  

### The JPEG files
The project's published facsimiles are JPEG files in Google Cloud, in a Cloud Storage Bucket. The images delivered to the project by the National Archives' scanning unit are on the project's network disc.  

## The publishing process

### Adding new content to the database from the spreadsheet
Documents are best added by archive unit (miscellaneous documents) or by part (letters and telegrams); the project is divided into 9 chronological parts (called "collections"). If the editors tell you that all documents from archive folder 58 or all letters/telegrams for part 6 have now been registered in the spreadsheet, you can start adding these documents.  

Only add archive documents whose images have been registered. Images are mainly registered only if they're in the National Archives and if we have a copy of them. Documents in the Leo Mechelin digital archive have to consist (as a minimum) of either images and metadata or text content and metadata, and if we don't have any notion of the images, how's the text content going to get transcribed? Ask the editors to fill in what they can and then just ditch all rows still lacking image info. Unless we're talking about articles and printed works, whose facsimiles are usually somewhere else than in the National Archives. But these genres aren't added through the spreadsheet anyway; we'll get to that later.  

The spreadsheet is not in a version control system. When new archive documents are to be added to the database from the spreadsheet, you need to download it and start working with that version locally. Once you've done that and once stuff has been added to the database, there's no real connection to the main spreadsheet and no easy way to know whether document info already added has been edited afterwards in the spreadsheet. If it has, those changes will probably never make it anywhere else, and the editors know that. The point is to cleanse, enrich and correct only the data going into the database from the local copy, and then update that data only in the database. The main spreadsheet isn't updated by the publishing process, it just gives us the raw data. It can eventually be left to its rightly earned destiny: destruction.  

#### Adding letters/telegrams according to part
Start by doing some standard operations to your local copy of the spreadsheet:  

**Chronological sorting (by hand)**: e.g., part 6 includes content from 1.4.1903 to 30.11.1905. Copy all rows with date 1903–1905 to a new sheet; now you have every document belonging to part 6 (and a little more). Then sort them according to genre: remember that there might be typos in the genre values! Copy everything which is a letter or telegram (also postcards etc.) to yet another sheet. Go through these rows and ditch the ones with dates 1.1–31.3.1903 (already added to part 5) and 1.12–31.12.1905 (going into part 7). Keep the ones with a date of just 1903 (since their last possible date is 31.12.1903), but ditch the ones dated just 1905 (they should be in part 7 since their last possible date is 31.12.1905). Check that this method is consistant and that the letters with date "1903" haven't been added to part 5. Also observe that a few letters already may exist for part 6: these possibly were added to an earlier part but in the editing process it was found that the registered date was wrong and therefore they have been moved. Or they belong to another archive and have therefore been added in bulk earlier on. There's a separate list of these letters from other archives you can consult in order to not add them twice.  

Letters and telegrams (from now on I'll just call them letters) are **divided into sent and received**. The scripts add one category at a time, so now you should separate the letters into these two categories and keep these on separate sheets.  

**Letters where both sender and recipient is someone else than Mechelin** are categorized in the db as received letters, since they obviously ultimately ended up in Mechelin's hands. But in the spreadsheet they were originally called just letter, "kirje", so make sure that's their genre; that's what the script for adding received letters is expecting. Their title value also has to be Person 1–Person 2 (with En Dash, e.g. Georg Rosenius–Robert Lagerborg, names in their usual form used elsewhere in the spreadsheet). If these two criteria are met, these documents will get added and connected correctly by [populate_publication_received_letter.py](https://github.com/Movanna/database_population?tab=readme-ov-file#3-a-populate_publication_received_letterpy).  

**Check all columns** for strange content. Are the **dates** acceptable? A lot of cases are handled by the scripts, but you might want to correct something, such as using En Dash in dates of type "1904–1905" and changing "1880/90" and "1880-tal" to "1880–1890" and "1880-talet". Fix typos in the **genre values** and change all dubious values ("postcard", "Christmas card" etc.) so that you only have e.g. sent letter and sent telegram left. The scripts can only handle one genre value (the standard case), but there might be several for a single document. If so: decide on the main value and edit out the other one(s). Keep a copy of the row and add the other value(s) afterwards, if they seem sensible. Check the **persons**. The scripts can only handle one sender or recipient (the standard case), so if there's more than one of each involved, you have to edit out the second person and keep a copy of the original row somewhere else. Then you can add the second person to the db later by hand. Typos in names are not a problem, as long as the person is in name_dictionary with this particular spelling (more info below). Also check the values for **archive unit** and delete everything in that cell which isn't a unit. If there are two archive units ("54 LM/KA; 116 LM/KA") I change the semicolon between them to a comma.  

Check that there's a **language** value for most letters. It's ok to have a few documents with language "unknown", i.e. missing, but in at least 99 % of the cases the language is easy to identify. If language values have been categorically left out of the spreadsheet (this has happened), they need to be fixed before adding anything to the database, as they're really important and will appear in many places, making it time-consuming to fix them afterwards. If there's more than one **language** for the letter, the languages have to be in a specific order: first the one that isn't sv or fi. E.g. "ruotsi, ranska" should be changed to "ranska, ruotsi". Or rewrite the script to fix this. Also keep in mind that language values are meant to describe the original language(s) of a single archive document, the main version of this document, which is made into a "publication" when added to the db. So if a letter has a substantial amount of content in another language than the main one, this should be registered. E.g., a letter mainly in French containing some paragraphs (not just words) in Swedish. If this letter is then translated into Finnish, this doesn't change its language values, because they only describe the *original* document. And if there is an original *version* of this letter, e.g. a draft from a notebook, the version is never transcribed, only added as an alternative facsimile. Even if this draft is in German, this isn't registered in the language values, since they only refer to the *main* version of the document.  

**The image signums** are going to give you the most trouble. The scripts for finding images based on the image signums work with either an old or a new image signum, so you need to keep these cases separate. This was based on the fact that in the beginning, all received letters had an old signum (which can be derived from the URL) and all sent letters a new one. But then things started to get mixed up and now there are both signums for both types. And the logic for finding the images is quite different depending on signum type.  

As stated in the section about the spreadsheet, image values may be easy or complicated, depending on whether the images are in order or not. If you for a new signum see only one value for the first image and one value for the last image, everything is fine. Likewise, if the signum is old and there's just one URL: excellent. But if you have several values you need to keep a copy of the original row and then edit the values into just one start value and one end value. The rest has to be fixed by hand later on. The same goes for alternative facsimiles: one alternative facsimile can be added automatically (if the values are uncomplicated), but if there are more versions than just one, you have to add those separately by hand. And if the version facsimiles are to have titles differing from the one of the original facsimile, you have to edit these titles separately in the db afterwards: keep a copy of the row and delete the titles from the sheet, just leaving the image values.  

**Add some standard columns to your sheet.** I made the scripts to expect a certain number of values for all rows, and I also add some empty placeholders beforehand for values the scripts will add. A signum for an alternative facsimile also has to be edited a bit for the scripts to work properly (you could of course rewrite the script). Check the example Excel file/CSV files for reference.  

**Save your sheet as CSV (encoding UTF-8).** Then (I usually do this in VS Code): find and replace leading/trailing whitespace in values, straight quotation marks/apostrophes, wrong dashes.  

Then **run the appropriate find_facsimiles-script**, found [here](https://github.com/Movanna/database_population?tab=readme-ov-file#2-find-the-images-for-each-document), which will add the file paths to the images (everything between first and last image) and modify the signums and image info. If you had some complicated image cases, now is the right time to get them sorted out: you can put the image file paths in the right order in the CSV, add missing file paths, or delete some. Just rememeber that you still have to fix some values for these cases in the db afterwards: "number_of_pages" and "page_comment". If you have two CSVs, one for letters with old and one for letters with new signums, you can merge these files once all image file paths have been found.  

With this one and only all-sent/received-letters-with-image-filepaths-CSV you can now proceed to **populating table publication** with either [populate_publication_sent_letter.py](https://github.com/Movanna/database_population?tab=readme-ov-file#3-b-populate_publication_sent_letterpy) or [populate_publication_received_letter.py](https://github.com/Movanna/database_population?tab=readme-ov-file#3-a-populate_publication_received_letterpy). Each script also creates all the needed XML files for the publication (and its manuscript, if needed) and updates the db with those file paths. The scripts also construct the titles for the texts and add a template to each XML file. Take a look at the README in the project's private repo for a description of the logic behind the creation of the files and folders, and check out the comments in the scripts.  

**I strongly recommend trying the script on the test db first.** This way you can catch all oddities, such as persons not identified or weird dates and missing language values. If you get unidentified persons where there actually is a name in the CSV, you can:  
- check that the person exists in name_dictionary.json (with the exact same spelling as in the spreadsheet)   
- if there's another version of the name in name_dictionary: fix the spelling in the CSV or, preferably, add the new name version to name_dictionary so that the person gets found the next time this spelling occurs  
- if the person isn't in name_dictionary at all: check whether he/she is in the db  
- if the person is in the db but not in name_dictionary and you got an unidentified person in your test title/files/folders: add this person and his/her ID to name_dictionary  
- if the person isn't in the db: add him/her to the db and to name_dictionary
- keep in mind that persons' names may be written differently in Swedish and Finnish: if this is the case for the person you're adding to the db, you need to add a row in table translation and four rows in table translation_text, as all persons with a Finnish translation (the Swedish name form is the standard, this is the one used in table subject) have four required attributes: "first_name", "last_name", "preposition", "full_name"; if the values don't differ from the Swedish ones (e.g. the preposition is "von" in both languages), use NULL
- you can also add the person's ID directly to the CSV; this way the person's name will be fetched directly from the db (for this document only, though) and you neither need to add the name to the spreadsheet/CSV, nor the connection between name and ID to name_dictionary; the scripts also handle translated names  

If you get incomplete/odd-looking names in your letter titles, such as just a surname, you can:  
- check the db entry for this person; if it has more content than your result:  
- fix the person's entry in Personregister.csv  

Names are mainly fetched from Personregister.csv and usually not directly from the db. This is because of the initial db structure and the editors' wishes: persons' names were to be registered in the titles of the letters, but not necessarily with what corresponds to the db fields "first_name", "last_name", "full_name", "alias", "alternative_form", but with a "letter name". At the time, I didn't want to add yet another attribute to the db, but I probably just should have. But I also thought that nearly all persons were already registered and that their names were not going to change. Unfortunately, this was not the case. But new persons added to the db only have to be added to name_dictionary, not to Personregister.csv. And as stated above, they can also be fetched solely based on an ID given in the CSV, but then you first have to add the ID to each affected row.  

Once you've gone through the initial test results and fixed your problems:  
- delete the XML files you got from running the script on the test db  
- make sure you've set the script's variables right: collection_id, csv_in etc.  
- run the script on the production db  
- move the resulting XML files and their folders to the appropriate folder in the project's private repo.  

Fix things afterwards:  
- add connections to persons not initially registered, such as an extra recipient, and edit the title of the letter accordingly (both sv and fi titles), I have used this model: "22.5.1860 LM–Gustaf & Amanda Mechelin"  
- edit Finnish titles in table translation_text if the Swedish title contained e.g. "våren 1904"; change it to "keväällä 1904"  
- edit date values in table publication for titles like the one above: this title automatically gets a date value of 1904-XX-XX, but you should change that to something like 1904-05-XX, or otherwise the TOC sorting will give this publication its last possible date, i.e. 31.12.1904, and the document will appear in the wrong place chronologically on the website
- add a second genre value not initially registered to table publication, if the publication belongs to several genres
- check for language value "xx" and try to identify the language for the document, and then update the value in tables publication and publication_manuscript as well as in the name of the XML file and in its file path in translation_text; "xx" should only be used for cases where the language really can't be identified, and not because someone just couldn't be bothered to fill in this information  

Now you can **update table publication with a "publication_group_id" for each letter**: use [add_publication_group.py](https://github.com/Movanna/database_population?tab=readme-ov-file#5-d-add_publication_grouppy) for that. Groups were not settled on when I first started adding publications, so this fixes lacking group IDs. Or rewrite the publication-adding script into also adding groups.  

You can now proceed to **populating table publication_facsimile_collection**, described [here](https://github.com/Movanna/database_population?tab=readme-ov-file#4-populate-table-publication_facsimile_collection-and-create-the-image-files) and creating the image files. Again, it's a good idea to try this on the test db first. Check for any suspiciously large facsimiles: letters typically don't consist of that many images. If a facsimile's number_of_pages is something like 10 or above, maybe the document's last page has been estimated wrong (old image signums), or there's a typo in the first or last image value (new signums).  

Once you've gone through the initial results and fixed the problems:  
- delete the folders and files you got from running the script on the test db  
- make sure you've set the script's variables right: facsimile_type, csv_in etc.  
- run the script on the production db  
- copy the resulting image files and their folders to the Cloud Storage Bucket  

Fix things afterwards: 
- separately add alternative facsimiles nr 2 and upwards, and edit the title of nr 1: alternative facsimiles automatically get the same title as the original but with an initial "Version" added, but if there are several versions they should be called "Version A", "Version B" etc.
- create the images for these facsimiles with [create_facsimiles.py](https://github.com/Movanna/database_population?tab=readme-ov-file#5-a-create_facsimilespy) and follow the steps later in this README for adding a facsimile  
- if an alternative facsimile comes from another archive unit than the main facsimile: edit the "description" value as well as the archive unit value in "external_url", both in table publication_facsimile_collection, since alternative facsimiles automatically get the main facsimile's archive unit value (or rewrite the script; but the usual case is them coming from the same unit)  
- if a document has facsimiles (including version facsimiles) from several archive units: edit the value for "archive_signum" in table publication into containing both signums, separated by a semicolon: "1900419.KA, 1493081994, 111 LM/KA; 1900420.KA, 1493081677, 111 LM/KA"  
- the logic for archive signums thus is: table publication holds all archive signums connected to a publication, and each facsimile only has its own signum, not the ones of other facsimiles for the same publication  
- if the image file paths were changed by hand in the CSV, you should check the actual number of images for the facsimile and update "number_of_pages" in publication_facsimile_collection, because it's going to be wrong (the script gets this number out of first and last image value, not by counting the actual number of file paths)  
- if the (order of the) image file paths were changed by hand in the CSV, you should also update "page_comment": if the actual image order isn't "1–10" (based on first image value, last image value) but "1–7, 9–10, 8", then that's what page_comment should say  

Now you can **create an updated table of contents** for the part you've added stuff to: [crete_new_toc.py](https://github.com/Movanna/database_population?tab=readme-ov-file#7-b-create_new_tocpy). Then copy the TOC JSON files to the project's private repo. Once the web server has pulled the latest content, you should see all newly added letters online: in TOC, as facsimiles, and as data in the metadata column. Then it's up to the editors to add the text content.  

#### Adding documents according to archive unit
Start by doing some standard operations to your local copy of the spreadsheet:  

**Sort the spreadsheet** firstly according to archive unit and secondly according to genre. Remember that the cell for archive unit also may contain other info and the sorting will therefore work only partly. If you are to add documents from e.g. archive folder 52 LM/KA, then copy those rows to a separate sheet. Then delete all letters/telegrams belonging to upcoming parts whose letters haven't yet been added (since letters are added separately by part, not by archive unit). However, if there are letters chronologically belonging to parts whose letters already have been added: check that these letters actually exist in the db/on the website. Ask the editors! If this archive unit's content were registered in the spreadsheet after the letters for say parts 1–3 were added to the db, then this unit contains unpublished letters that need to be added too. Since the main spreadsheet gets updated all the time with new content, you'll inevitably end up with these cases of new letters being found, even though they belong to already published parts. Use the letter adding process for these letters and add them to the earlier parts ("collections").  

Study the instructions for the letter adding process carefully and follow the same steps, but with these changes:  

If any of the **genre values** isn't present in genre_dictionary, you need to add it. Observe that there are more genre values used in the spreadsheet than in the db: genre_dictionary makes for instance "teatteri" and "meny" into db genre "dokument", so think carefully about what value to use and if you want to merge it into an existing category. If you add new genre values to the db, they also have to be added to the search engine or they won't show up in the search. new_genre_dictionary contains the values currently in use in the db and in the search engine. I suspect these values are enough. Remember that the scripts only handle one genre value: if you have more than one, keep a copy of the row and fix the lacking value afterwards.  

It's also possible that some documents/genres from this archive unit already have been added, even though the archive unit as a whole hasn't. This is because articles, printed works, some speeches and some poems have been given to me on separate lists and added no matter what their archive unit was. It's also possible that an entry, especially for any of these genres, should be added as a version facsimile to an already existing document. If the genre value is "käsikirjoitus", this is probably the case. Or if otherwise stated that this is the manuscript to e.g. an article. Check these cases carefully and ask the editors!  

In the spreadsheet there's a cell for **author**, but it's often empty. When adding publications categorized as "misc" (mostly manuscripts of sorts, the ones registered in the spreadsheet as anything but letter/telegram/article/work), no value will result in a connection in the db to "unknown author", and this will show up in the metadata for the document on the website. You should try to connect texts to authors. Maybe the author is Mechelin himself? What does the document look like, is it in his handwriting? Sometimes the title field or another field says something about the author, then you should add the author's ID to the author cell (and possibly edit the title). The author part often needs some investigation. Ask the editors! Some genres, such as newspaper clippings, rarely have known authors, so for these "unknown author" is totally fine. But you can also change the author connection afterwards; if you spend too much time on it now, you won't get many documents added. As in the case of letters, if there's more than one person involved, you need to make a copy of the row, then edit the row into containing just one ID, and then fix this afterwards in the db. If Mechelin is the **co-author** of a document, this should be registered as e.g. "/7804", a slash followed directly by the ID for the other author. Or just a slash, if the other co-author is unknown.  

The **titles** also need some special attention. The title value isn't necessarily thought through, or it contains typos or otherwise needs editing. If the title is in the Cyrillic alphabet, keep a copy of the row and add a standard Swedish title such as "ryskt dokument". The titles will appear in the file and folder names and those should only be in the Latin alphabet. You can then add the Russian title afterwards in the db. If there's both a sv and a fi title given in the spreadheet, in the title cell, I'd normally edit out the other one.  

**Languages, image signums and alternative facsimiles** follow the same rules as for letters. About languages: even though the language value should only describe the main version of the archive document (if it even has versions), this isn't always the case in the spreadsheet. E.g., Mechelin's book "Finland i 19de seklet" exists in several different language versions, such as Swedish, Finnish, English and Russian, printed separately as separate versions of the same text. However, this doesn't mean that the language values should be registered in the db as "en, ru, sv, fi", as that indicates a *single* text, within the same document, written in those four languages.  

Follow the same steps as for letter for **saving as CSV** and **running the appropriate find_facsimiles-script**.  

You can now proceed to **populating table publication** using [populate_publication_misc.py](https://github.com/Movanna/database_population?tab=readme-ov-file#3-e-populate_publication_miscpy). The script adds content to one part (by collection_id) at a time. In the beginning, misc documents were to be added according to part, and I wrote the script accordingly. Then I realized it was much better to add these documents according to archive unit, because otherwise there was no way of knowing for sure what had been added when the main spreadsheet kept getting updated with new archive units. So, because of this legacy, you should split your CSV into one for each part before running the populating script.  

The same steps as for letters still apply: **use the test db first**! But since authors are fetched directly from the db according to their ID in the CSV, you'll have less trouble with names.  

The steps for **updating group_id** and **populating table publication_facsimile_collection** are the same as for letters.  

For fixing things afterwards, there's two additions:  
- I always edit out the date from the version facsimile title, unless it's a letter, since the date comes from the original and the version probably/possibly was written on another date. So original facsimile title "1903 Bör Du blifva soldat?", version facsimile title "Version / Bör Du blifva soldat?"
- alternative facsimile titles may be in Finnish if that facsimile is in Finnish, but the word "Version" has been kept as it is: "Version B / Arvoisat kansalaiset!" or "Version E (finska) / Värnpliktsadressen"  

Also keep in mind that titles in the spreadsheet usually are in the archive document's original language. Since every publication in this edition needs a Swedish or a Finnish title if it has text content in sv or fi, you'll need to edit the titles in table translation_text once the texts have been translated. Naturally, the script initially adds the same title for both language versions, otherwise half of the documents wouldn't have a title at all (since it's unknown at the moment). You can update the titles in tables publication_manuscript and publication_facsimile_collection using [update_title_and_signum.py](https://github.com/Movanna/database_population?tab=readme-ov-file#5-c-update_title_and_signumpy); these titles are the same as the sv title in translation_text, so fix that one first and the run the script. It doesn't update version facsimile titles, because we just stated that they could have special titles, differing from the original title.  

### Adding articles, printed works and hansards
For these genres I've received separate lists, so they haven't been added using the main spreadsheet. If the facsimiles are kept elsewhere than in the National Archives, there's very little information required for the CSV. Simply use [populate_publication_article.py](https://github.com/Movanna/database_population?tab=readme-ov-file#3-c-populate_publication_articlepy) or [populate_publication_hansard.py](https://github.com/Movanna/database_population?tab=readme-ov-file#3-f-populate_publication_hansardpy), one part (collection_id) at a time. Then add the facsimiles (often a linked facsimile) separately; se further below for how-to.  

The script adds all of these with "original_language" Swedish, since that's the normal case. If the article is in another language, follow these steps after its addition: change its language in table publication, create a new XML file with the correct language value and add it to the corresponding folder in the project's private repo. Articles in foreign languages are in publication_manuscript, add the article with this type of query:  

`INSERT INTO publication_manuscript(publication_id, deleted, published, original_filename, name, type, original_language) VALUES(14485, 0, 1, 'documents/Delutgava_4/Artiklar/Revue_Politique_et_Parlementaire/1896_XX_XX_Finlande/1896_XX_XX_Finlande_fr_14485.xml', '1896 Finlande.', 5, 'fr');`  

Or rewrite the script to handle articles in foreign languages. But I don't think it's worth it, most articles should have been added by now anyway.  

### General things to do after the addition of new archive documents
Things you might need or want to to after adding new content are described [here](https://github.com/Movanna/database_population#5-fix-things-afterwards-and-tidy-up-the-db).  

### Transforming text content
A common task is to convert a word processor document into the kind of XML this project uses. Another common scenario is to receive XML files exported from Transkribus. For both of these cases, take a look at the README in [transform_texts](https://github.com/Movanna/transform_texts) and then use [transform_xml.py](https://github.com/Movanna/transform_texts#1-a-transform_xmlpy).  

Here are some hints for transforming texts:  
- DOCUMENT_TYPE is for choosing which kind of document you want to transform: letter, article, misc. "article" includes any printed works, plus introductions. "misc" is basically everything which isn't a letter or an article or a printed work, mainly manuscripts or miscellaneous documents (that also may be (partly) printed).  
- the choice of DOCUMENT_TYPE will affect the outcome substantially: "article" will produce a result with paragraphs containing reflowable text instead of e.g. 15 lines per page, some of them are ending with a hyphen. This transformation thus makes all line breaks, end-of-line hyphens and newlines within paragraphs disappear tracelessly. "misc" on the other hand will preserve all original line breaks within paragraphs and add the required `<lb/>`-tags, since these manuscripts are to be encoded line by line in this project.  
- CHECK_UNTAGGED_ABBREVIATIONS is for adding expansions to any word in the document that is present in the abbr_dictionary. If False, then only `<choice><abbr>`-encoded words will get expansions from the dictionary.  
- in do_not_expand you can keep a list of words that only should be given expans if they have been encoded as `<abbr>`, otherwise they probably aren't abbrs but just ordinary words, even though present in the dictionary. E.g. "del." can be an `<abbr>` for "delgavs" and is therefore in the dict, but unless `<abbr`>-encoded it's probably just a normal word followed by a full stop.  
- CORRECT_P is for material from Transkribus where you don't want to keep the default `<p>`-elements. Set it to True if you prefer adding all of your paragraphs yourself. Transkribus tends to add paragraphs in a very unconsistent way and this gives you the option to ignore those.  
- if exporting TEI XML from Transkribus: make sure to use export option `<lb/>`/TEI XML and don't correct anything manually, or if you do: don't get rid of the default tabs/spaces at the beginning of each line since the script is expecting them
- in the outcome: search for all `<abbr>` and go through them. If there are many wrongly interpreted or unexpanded `<abbr>`-elements, you might want to update the abbr_dictionary and run the script again in order to get a better outcome. Since each distinct `<abbr>` only can be given one `<expan>` in the dict, the result is rarely perfect and needs attention anyway. Regex is often meaningful to use in order to fix the final results in the file.
- also check the general outcome: are line breaks preserved or removed as you wanted? If not, check the input file or your script variables.
- other things to check in the outcome: numbers (the script adds Narrow No-break Space in numbers over 999, but you might want to make sure that this hasn't been added in a year/date), fractions (often not encoded correctly in the original file, so search for "/" and replace 1/2 with ½ or with the proper XML elements for superscript and subscript; also make sure that alternative dates (Julian + Gregorian with a slash between them) are not fractions), headings (the script uses an @level counting from the top heading downwards, since it's often hard to get the hierarchy right in the original; replace these with the proper attibute), footnotes; and then the usual editing problems such as the correct use of whitespace in abbreviations and around dashes and so on  

### Recurring database operations

#### Correct a person's name in a letter title
The editors may ask you to **correct a name in a letter title**. The titles and the files and folders for each publication are created once and not updated automatically. If a person's name is changed in the db, you need to update all titles containing this name, and perhaps also the files and folders and the file paths in the db.  

Fetch publications connected to a certain person and check if the name in the publications' titles and file paths match the current version of this person's name in table subject:  

`SELECT publication.id,`  
    `CASE`  
        `WHEN translation_text.field_name = 'name' THEN translation_text.translation_id`  
    `END AS "translation_id",`  
    `CASE`  
        `WHEN translation_text.language = 'sv' AND translation_text.field_name = 'name' THEN translation_text.text`  
    `END AS "title",`  
    `CASE`  
        `WHEN translation_text.language = 'fi' AND translation_text.field_name = 'name' THEN translation_text.text`  
    `END AS "title_fi",`  
`publication_manuscript.original_filename, publication_manuscript.original_language, subject.first_name, subject.preposition, subject.last_name, subject.full_name,`  
    `CASE`  
        `WHEN subject.translation_id IS NOT NULL AND translation_text.language = 'fi' AND translation_text.field_name = 'full_name' THEN translation_text.text`  
    `END AS "full_name_fi",`  
    `CASE`  
        `WHEN subject.translation_id IS NOT NULL THEN subject.translation_id`  
    `END AS "name_translation_id"`  
`FROM publication`  
    `LEFT JOIN`  
        `event_occurrence ON publication.id = event_occurrence.publication_id`  
    `LEFT JOIN`  
        `event_connection ON event_occurrence.event_id = event_connection.event_id`  
    `LEFT JOIN`  
        `subject ON event_connection.subject_id = subject.id`  
    `LEFT JOIN`  
        `publication_manuscript ON publication_manuscript.publication_id = publication.id`  
    `LEFT JOIN`  
        `translation_text ON (publication.translation_id = translation_text.translation_id AND translation_text.field_name = 'name') OR (subject.translation_id = translation_text.translation_id AND translation_text.field_name = 'full_name')`  
`WHERE subject.id = 1229;`  

Keep in mind that some persons were deliberately added to titles with their "letter name", which isn't in the db at all! So even if the name info in the db and in the title don't match, everything might still be ok (can be checked in Personregister.csv). But if you've been asked to change the title, then this probably isn't the case.  

Correct the occurrences in the titles in the db. Keep in mind that names may have a translation: if that's the case, then the sv and fi titles should differ. If there's just a minor change in the name, such as "A. Edelfelt" being changed to "Albert Edelfelt", you don't need to change the names of the files/folders. But if the change is significant, you should also update the files/folders, or otherwise the editors will have a hard time finding the right files since all letter folders/files contain the sender's/recipient's name. You can do this with [delete_or_rename_files.py](https://github.com/Movanna/database_population?tab=readme-ov-file#5-g-delete_or_rename_filespy). Remember to also update the file paths in the db, in tables translation_text and publication_manuscript.  

Finally update Personregister.csv with the new name info (if the person is present in that CSV), otherwise this person will still get added with the old name next time you add new documents to the db. And update the titles in tables publication_manuscript and publication_facsimile_collection using [update_title_and_signum.py](https://github.com/Movanna/database_population?tab=readme-ov-file#5-c-update_title_and_signumpy).  

#### Delete a duplicate person/merge two persons
Use the query above to check whether either one of the person IDs has titles linked to them. Check if there are any other connections for either person in table event_connection. Check if either ID has been used in the XML files, as the value for @corresp in `<persName>`. Then set one of the IDs to deleted and fix all resulting issues. Also change the reference ID in name_dictionary for the deleted person.  

#### Correct a date
Every title contains a date. The date in the title can sometimes be in a rather free form, such as "våren 1890". The automatically given "original_date" value for that would be "1890-XX-XX", which is in table publication, and in the names of the files and folders for this document, as "1890_XX_XX". If you are asked to correct a date, fix the value in table publication and in the title in table translation_text. If a printed work gets an exact date instead of just a year, you don't have to update its files/folders, since XML files for works are few and easy to find anyway. But for all other genres, you should always update the files/folders if there are any changes to the date, or otherwise the editors will have a hard time finding the right files. Remember to also update the file paths in the db, in tables translation_text and publication_manuscript (if present). You can update the titles in tables publication_manuscript and publication_facsimile_collection using [update_title_and_signum.py](https://github.com/Movanna/database_population?tab=readme-ov-file#5-c-update_title_and_signumpy). Keep in mind that a changed date also may lead to moving the document from one part/collection to another, or a changed publication group. If the former is the case: change "collection_id" in table publication, move the files/folders in the project's private repo, update the file paths with a new collection_id. If the latter is the case, change "publication_group_id" in table publication.  

#### Connect a person to a publication
Connect a person to a publication from scratch: steps 1–3. Persons are in table subject.  

Usually there's already an event and an occurrence, and you only need to update an existing connection, or add a new connection if we're dealing with e.g. a letter with two senders instead of one. Mechelin being the author/sender/recipient is implicit and not registered in the db, unless he's one of several authors/senders/recipients. So if you are to change a connection from Mechelin to another person, then you'll have to go through all 3 steps, because the Mechelin connection isn't physically in the db, it's the result of there not being any other connection. I thought this would keep the db lean, and why add something that can be queried anyway, without the info being explicitly there?  

1. Add an event:  
`INSERT INTO event(deleted, type) VALUES(0, 'published') RETURNING id;`  
2. Add an event occurrence. The event_occurrence type is always from LM's point of view, so type "sent letter" means a letter he sent and someone else received:  
`INSERT INTO event_occurrence(deleted, type, event_id, publication_id) VALUES (0, 'sent letter', 6835, 1957) RETURNING id;`  
3. Add an event connection. The event_connection type is always from the connected person's point of view, so type "sent letter" means a letter this person sent:  
`INSERT INTO event_connection(deleted, subject_id, event_id, type) VALUES(0, 1, 12946, 'sent letter');`  

#### Add a new facsimile
Add a new facsimile **consisting of image files** and connect it to a publication: steps 1–5.  

1. Create the facsimile images using [create_facsimiles.py](https://github.com/Movanna/database_population?tab=readme-ov-file#5-a-create_facsimilespy).  
2. Add the new facsimile:  
`INSERT INTO publication_facsimile_collection(title, number_of_pages, start_page_number, description, folder_path, page_comment, external_url)`   
`VALUES('21.9.1901 Ebba zu Solms-Braunfels–LM', 1, 1, '1886832.KA, 1493080018, 115 LM/KA', '/facsimiles', '225', 'https://astia.narc.fi/uusiastia/digitarkastelu.html?id=1493080018') RETURNING id;`  
3. Connect it to the publication and set whether it's an alternative facsimile or not, and what type of document it is:  
`INSERT INTO publication_facsimile(publication_facsimile_collection_id, publication_id, page_nr, section_id, priority, type) VALUES(20145, 14484, 0, 0, 1, 1) RETURNING id;`
4. Rename the facsimile folder after its publication_facsimile_collection ID and copy it to the Cloud Storage Bucket.
5. If the newly added facsimile has a different archive unit than the previous facsimile(s): edit the value for "archive_signum" in table publication into containing all signums, separated by a semicolon: "1900419.KA, 1493081994, 111 LM/KA; 1900420.KA, 1493081677, 111 LM/KA"  

Add a new facsimile **that doesn't have image files, only a link to another archive containing the images**, and connect it to a publication: steps 1–3.  

1. Add the new facsimile:  
`INSERT INTO publication_facsimile_collection(title, description, external_url) VALUES('<cite>Helsingfors-Posten</cite> 10.7.1903, nr 184', 'KK', 'https://digi.kansalliskirjasto.fi/sanomalehti/binding/628144?page=4') RETURNING id;`  
2. Connect it to the publication and set whether it's an alternative facsimile or not, and set type to 0 (linked images only):  
`INSERT INTO publication_facsimile(publication_facsimile_collection_id, publication_id, page_nr, section_id, priority, type) VALUES(20147, 14486, 0, 0, 1, 0) RETURNING id;`
3. Update the "archive_signum" value in table publication, because this is where you set the info for the archive source for this publication. Values for linked facsimiles are typically "KK" (Kansalliskirjasto), "Gallica" or "Google Books". If you add a completely new archive source it also has to be registered in the the project's private repo's equivalent of [this script](https://github.com/Movanna/database_population#6-a-api_endpointspy), because the API endpoint for the metadata transforms and translates these db values, they're not displayed as such on the website.  

#### Fix an existing facsimile for a received letter
Initially, facsimiles were registered in the spreadsheet by a single URL, which led to the first image of the document in the National Archives' digital archive. Out of this URL it's possible to construct the file path to the corresponding image on the project's network disk. However, since the document's last image wasn't registered in the spreadsheet, the last image for most of these documents is a qualified guess based on the next document's first image, in the same archive unit, that is. About 60 % of these facsimiles are correct, and the rest has either too few or to many images. Too few, when the last page is in the same image as the next document's first image (the script stops at the image before that, which is the most logical one). Too many, when the part (letters are added according to part) ends before the year end, because archive units often contain one or more year's letters for one sender. If there's no next publication to stop the script, it will simply assume the current document contains all remaining images in the archive unit/image folder. What else could it do?  

Since the script has sorted letters according to archive units in order to get the facsimiles as good as they get, it's at least easy to know where missing images are: in the next publication's facsimile unit. Next here meaning the following "publication_id". So if a received letter ends abruptly, check the next publication_id's facsimile:  

1. Find the facsimile for the publication with a flawed facsimile:  
`SELECT publication_facsimile_collection_id FROM publication_facsimile WHERE publication_id = 13035;`  
2. In table publication_facsimile_collection, check the next row counting from your result. This is where you'll probably find the missing image, as nr 1 in this facsimile unit. Check this on the website by inspecting the facsimiles for said publications.  
3. In the Cloud Storage Bucket, copy the image from the second folder (the one one with an ID that's usually one step higher) to the first one (the one with the ID you were first looking for), renaming it if necessary, since all images should be named 1, 2, 3, 4 etc.
4. Update values "number_of_pages" and "page_comment" in table publication_facsimile_collection.

If necessary, you can also move an image from one folder to another in the Cloud Storage Bucket. In that case, remember to update "number_of_pages" and "page_comment" for both facsimiles! I fix everything in the Cloud Storage Bucket and nowhere else, even though I have kept the initial facsimile folders on the network disk as some kind of backup.  

#### Connect a translator to a publication
Connect a translator to a publication and set the language of the translation:  
`INSERT INTO contribution(publication_collection_id, publication_id, type, text_language, contributor_id) VALUES(4, 11973, 'translation', 'fi', 17);`  

Publications with text content in a language that isn't the document's original language, lacking a connected translator, are found (by part/"collection") in the monthly report (produced by [this script](https://github.com/Movanna/transform_texts#4-a-content_length_and_statisticspy)) by sorting the sheet firstly on "teckenmängd" and secondly on "id". Then check for empty slots in the translator column. Fix these missing connections. Simultaneously, you can check that the titles for these publications are in the right language; they're on the same row in the monthly report. If not: update the title for the publication in table translation_text. If there are many translator-connections to add: ask the editors for a list containing collection_id, publication_id, translator, the language of the translation, the translated title.  

#### Delete a publication
Set the publication to deleted in tables publication, publication_manuscript (if present), translation_text (4 rows: 2 titles, 2 file paths). Also set to deleted (if present): the connected event in table event and the connections in tables event_connection and event_occurrence, the facsimile in publication_facsimile_collection and the connection in table publication_facsimile. You can keep the facsimile folder in the Cloud Storage Bucket, or delete it; lately, I haven't bothered to delete them.  

#### Publish a collection externally
Set all publications in a collection to externally published:  
`UPDATE publication SET published = 2 WHERE publication_collection_id = 4 AND deleted = 0;`  

You also have to update "published" in publication_collection, publication_collection_title and publication_collection_introduction, but not in publication_manuscript.  

Check/add the reference_text in table urn_lookup. Change "group_id" in table publication for all publications with a value corresponding to "unknown time period" to another group: a published collection should only have publication groups with actual date values, and if no other date can be set, then the publication should be in the last group of the last collection. Update the title page for the collection in the project's private repo. Update the static HTML (Md files, same repo) with the new statistics for the published content. For yet other steps needed: see the README in the project's private repo.  

### Create a monthly report
See [this description](https://github.com/Movanna/transform_texts?tab=readme-ov-file#4-find-out-the-length-of-the-text-content-in-xml-files-combine-it-with-database-data-and-do-some-automated-data-preparation-and-visualization).  

### Create a new TOC
You need to create an updated table of contents for the all parts ("collections") whenever publications have been added to or deleted from a collection or if a publication's title has changed. If a publication that so far only consisted of images has gotten text content, you should also update the TOC, or otherwise the "facsimile only" image will still show up, as this is set only in TOC. Use [crete_new_toc.py](https://github.com/Movanna/database_population#7-b-create_new_tocpy) to create the files. I usually open them in VS Code after the creation and choose "Format document" to pretty print them. Otherwise it's hard to spot the changes in the GitHub Diff. Then copy the JSON files to the project's private repo. It's good to give them a glance in the GitHub Diff to make sure everything is ok. Once the web server has pulled the latest content, you'll see the new TOC.  
