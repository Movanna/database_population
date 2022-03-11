-- --------------------------------------------------------
-- Verkkotietokone:              
-- Palvelinversio:               PostgreSQL 10.11 on x86_64-pc-linux-musl, compiled by gcc (Alpine 9.2.0) 9.2.0, 64-bit
-- Server OS:                    
-- HeidiSQL Versio:              11.3.0.6295
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES  */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Dumping structure for function public.check_original_publication_date
DELIMITER //
CREATE FUNCTION "check_original_publication_date"() RETURNS UNKNOWN AS $$ 
BEGIN
	IF NEW.original_publication_date ~* '([0-9X]{1,4}-[0-9X]{2}-[0-9X]{2}T?[]?)([0-9]{2}:[0-9]{2}:[0-9]{2})?(\+[0-9]{2}:[0-9]{2})?([ ]BC)?' OR NEW.original_publication_date IS NULL THEN
		RETURN NEW;
	ELSE
		RAISE EXCEPTION 'Invalid original_publication_date';
	END IF;
END;
 $$//
DELIMITER ;

-- Dumping structure for function public.check_subject_date_born
DELIMITER //
CREATE FUNCTION "check_subject_date_born"() RETURNS UNKNOWN AS $$ 
BEGIN
	IF NEW.date_born ~* '([0-9X]{1,4}-[0-9X]{2}-[0-9X]{2}T?[]?)([0-9]{2}:[0-9]{2}:[0-9]{2})?(\+[0-9]{2}:[0-9]{2})?([ ]BC)?' OR NEW.date_born IS NULL THEN
		RETURN NEW;
	ELSE
		RAISE EXCEPTION 'Invalid date_born';
	END IF;
END;
 $$//
DELIMITER ;

-- Dumping structure for function public.check_subject_date_deceased
DELIMITER //
CREATE FUNCTION "check_subject_date_deceased"() RETURNS UNKNOWN AS $$ 
BEGIN
	IF NEW.date_deceased ~* '([0-9X]{1,4}-[0-9X]{2}-[0-9X]{2}T?[]?)([0-9]{2}:[0-9]{2}:[0-9]{2})?(\+[0-9]{2}:[0-9]{2})?([ ]BC)?' OR NEW.date_deceased IS NULL THEN
		RETURN NEW;
	ELSE
		RAISE EXCEPTION 'Invalid date_deceased';
	END IF;
END;
 $$//
DELIMITER ;

-- Dumping structure for function public.trigger_set_timestamp
DELIMITER //
CREATE FUNCTION "trigger_set_timestamp"() RETURNS UNKNOWN AS $$ 
BEGIN
	NEW.updated_at = NOW();
	RETURN NEW;
END;
 $$//
DELIMITER ;

-- Dumping structure for table public.contributor
CREATE TABLE IF NOT EXISTS "contributor" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''contributor_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT '2018-10-12 09:12:28.144759',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"publication_collection_id" BIGINT NULL DEFAULT NULL,
	"publication_collection_introduction_id" BIGINT NULL DEFAULT NULL,
	"publication_collection_title_id" BIGINT NULL DEFAULT NULL,
	"publication_id" BIGINT NULL DEFAULT NULL,
	"publication_manuscript_id" BIGINT NULL DEFAULT NULL,
	"publication_version_id" BIGINT NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"type" TEXT NULL DEFAULT NULL,
	"first_name" TEXT NULL DEFAULT NULL,
	"last_name" TEXT NULL DEFAULT NULL,
	"description" TEXT NULL DEFAULT NULL,
	"prefix" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "contributor_deleted_idx" ("deleted"),
	INDEX "fk_contributor_publication_collection_id_idx" ("publication_collection_id"),
	INDEX "fk_contributor_publication_collection_introduction_id_idx" ("publication_collection_introduction_id"),
	INDEX "fk_contributor_publication_collection_title_id_idx" ("publication_collection_title_id"),
	INDEX "fk_contributor_publication_id_idx" ("publication_id"),
	INDEX "fk_contributor_publication_manuscript_id_idx" ("publication_manuscript_id"),
	INDEX "fk_contributor_publication_version_id_idx" ("publication_version_id"),
	CONSTRAINT "fk_contributor_publication_collection_id" FOREIGN KEY ("publication_collection_id") REFERENCES "public"."publication_collection" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_contributor_publication_collection_introduction_id" FOREIGN KEY ("publication_collection_introduction_id") REFERENCES "public"."publication_collection_introduction" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_contributor_publication_collection_title_id" FOREIGN KEY ("publication_collection_title_id") REFERENCES "public"."publication_collection_title" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_contributor_publication_id" FOREIGN KEY ("publication_id") REFERENCES "public"."publication" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_contributor_publication_manuscript_id" FOREIGN KEY ("publication_manuscript_id") REFERENCES "public"."publication_manuscript" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_contributor_publication_version_id" FOREIGN KEY ("publication_version_id") REFERENCES "public"."publication_version" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.correspondence
CREATE TABLE IF NOT EXISTS "correspondence" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''correspondence_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"legacy_id" TEXT NULL DEFAULT NULL,
	"title" TEXT NULL DEFAULT NULL,
	"description" TEXT NULL DEFAULT NULL,
	"source_collection_id" TEXT NULL DEFAULT NULL,
	"source_archive" TEXT NULL DEFAULT NULL,
	"source_id" TEXT NULL DEFAULT NULL,
	"material" TEXT NULL DEFAULT NULL,
	"material_color" TEXT NULL DEFAULT NULL,
	"material_type" TEXT NULL DEFAULT NULL,
	"material_source" TEXT NULL DEFAULT NULL,
	"material_quality" TEXT NULL DEFAULT NULL,
	"material_state" TEXT NULL DEFAULT NULL,
	"material_notes" TEXT NULL DEFAULT NULL,
	"language" TEXT NULL DEFAULT NULL,
	"date_sent" TEXT NULL DEFAULT NULL,
	"page_count" TEXT NULL DEFAULT NULL,
	"project_id" BIGINT NULL DEFAULT NULL,
	"correspondence_collection_id" BIGINT NULL DEFAULT NULL,
	"correspondence_collection_id_legacy" BIGINT NULL DEFAULT NULL,
	"material_pattern" TEXT NULL DEFAULT NULL,
	"material_format" TEXT NULL DEFAULT NULL,
	"leaf_count" TEXT NULL DEFAULT NULL,
	"sheet_count" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "correspondence_deleted_idx" ("deleted"),
	INDEX "fk_correspondence_correspondence_collection_id_idx" ("correspondence_collection_id"),
	INDEX "fk_correspondence_project_id_id_idx" ("project_id"),
	CONSTRAINT "fk_correspondence_correspondence_collection_id" FOREIGN KEY ("correspondence_collection_id") REFERENCES "public"."correspondence_collection" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_correspondence_project_id" FOREIGN KEY ("project_id") REFERENCES "public"."project" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.correspondence_collection
CREATE TABLE IF NOT EXISTS "correspondence_collection" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''correspondence_collection_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"title" TEXT NULL DEFAULT NULL,
	"description" TEXT NULL DEFAULT NULL,
	"source" TEXT NULL DEFAULT NULL,
	"start_year" TEXT NULL DEFAULT NULL,
	"end_year" TEXT NULL DEFAULT NULL,
	"legacy_id" BIGINT NULL DEFAULT NULL,
	"category" TEXT NULL DEFAULT NULL,
	"original_letter_amount" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "correspondence_collection_deleted_idx" ("deleted")
);



-- Dumping structure for table public.event
CREATE TABLE IF NOT EXISTS "event" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''event_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"type" TEXT NULL DEFAULT NULL,
	"description" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "event_deleted_idx" ("deleted")
);



-- Dumping structure for table public.event_connection
CREATE TABLE IF NOT EXISTS "event_connection" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''event_connection_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"subject_id" BIGINT NULL DEFAULT NULL,
	"tag_id" BIGINT NULL DEFAULT NULL,
	"location_id" BIGINT NULL DEFAULT NULL,
	"event_id" BIGINT NULL DEFAULT NULL,
	"work_manifestation_id" BIGINT NULL DEFAULT NULL,
	"correspondence_id" BIGINT NULL DEFAULT NULL,
	"type" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "event_connection_deleted_idx" ("deleted"),
	INDEX "fk_event_connection_correspondence_id" ("correspondence_id"),
	INDEX "fk_event_connection_event_id_idx" ("event_id"),
	INDEX "fk_event_connection_location_id_idx" ("location_id"),
	INDEX "fk_event_connection_subject_id_idx" ("subject_id"),
	INDEX "fk_event_connection_tag_id_idx" ("tag_id"),
	INDEX "fk_event_connection_work_manifestation_id_idx" ("work_manifestation_id"),
	CONSTRAINT "fk_event_connection_correspondence_id" FOREIGN KEY ("correspondence_id") REFERENCES "public"."correspondence" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_event_connection_event_id" FOREIGN KEY ("event_id") REFERENCES "public"."event" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_event_connection_location_id" FOREIGN KEY ("location_id") REFERENCES "public"."location" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_event_connection_subject_id" FOREIGN KEY ("subject_id") REFERENCES "public"."subject" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_event_connection_tag_id" FOREIGN KEY ("tag_id") REFERENCES "public"."tag" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_event_connection_work_manifestation_id" FOREIGN KEY ("work_manifestation_id") REFERENCES "public"."work_manifestation" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.event_occurrence
CREATE TABLE IF NOT EXISTS "event_occurrence" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''event_occurrence_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"type" TEXT NULL DEFAULT NULL,
	"description" TEXT NULL DEFAULT NULL,
	"event_id" BIGINT NULL DEFAULT NULL,
	"publication_id" BIGINT NULL DEFAULT NULL,
	"publication_version_id" BIGINT NULL DEFAULT NULL,
	"publication_manuscript_id" BIGINT NULL DEFAULT NULL,
	"publication_facsimile_id" BIGINT NULL DEFAULT NULL,
	"publication_comment_id" BIGINT NULL DEFAULT NULL,
	"publication_facsimile_page" BIGINT NULL DEFAULT NULL,
	"publication_song_id" BIGINT NULL DEFAULT NULL,
	"work_id" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "event_occurrence_deleted_idx" ("deleted"),
	INDEX "fk_event_occurrence_event_id_idx" ("event_id"),
	INDEX "fk_event_occurrence_publication_comment_id_idx" ("publication_comment_id"),
	INDEX "fk_event_occurrence_publication_facsimile_id_idx" ("publication_facsimile_id"),
	INDEX "fk_event_occurrence_publication_id_idx" ("publication_id"),
	INDEX "fk_event_occurrence_publication_manuscript_id_idx" ("publication_manuscript_id"),
	INDEX "fk_event_occurrence_publication_version_id_idx" ("publication_version_id"),
	CONSTRAINT "fk_event_occurrence_event_id" FOREIGN KEY ("event_id") REFERENCES "public"."event" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_event_occurrence_publication_comment_id" FOREIGN KEY ("publication_comment_id") REFERENCES "public"."publication_comment" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_event_occurrence_publication_facsimile_id" FOREIGN KEY ("publication_facsimile_id") REFERENCES "public"."publication_facsimile" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_event_occurrence_publication_id" FOREIGN KEY ("publication_id") REFERENCES "public"."publication" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_event_occurrence_publication_manuscript_id" FOREIGN KEY ("publication_manuscript_id") REFERENCES "public"."publication_manuscript" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_event_occurrence_publication_song_id" FOREIGN KEY ("publication_song_id") REFERENCES "public"."publication_song" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_event_occurrence_publication_version_id" FOREIGN KEY ("publication_version_id") REFERENCES "public"."publication_version" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_event_occurrence_work_id" FOREIGN KEY ("work_id") REFERENCES "public"."work" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.event_relation
CREATE TABLE IF NOT EXISTS "event_relation" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''event_relation_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT '2018-10-12 09:12:28.729647',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"event_id" BIGINT NULL DEFAULT NULL,
	"related_event_id" BIGINT NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	PRIMARY KEY ("id"),
	INDEX "event_relation_deleted_idx" ("deleted"),
	INDEX "fk_event_relation_event_id_idx" ("event_id"),
	CONSTRAINT "fk_event_relation_event_id" FOREIGN KEY ("event_id") REFERENCES "public"."event" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for view public.get_manifestations_with_authors
CREATE TABLE "get_manifestations_with_authors" (
	"json_data" JSON NULL,
	"project_id" BIGINT NULL
) ENGINE=MyISAM;

-- Dumping structure for table public.location
CREATE TABLE IF NOT EXISTS "location" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''location_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"name" TEXT NULL DEFAULT NULL,
	"country" TEXT NULL DEFAULT NULL,
	"city" TEXT NULL DEFAULT NULL,
	"description" TEXT NULL DEFAULT NULL,
	"legacy_id" TEXT NULL DEFAULT NULL,
	"latitude" NUMERIC(9,6) NULL DEFAULT NULL,
	"longitude" NUMERIC(9,6) NULL DEFAULT NULL,
	"project_id" BIGINT NULL DEFAULT NULL,
	"region" TEXT NULL DEFAULT NULL,
	"source" TEXT NULL DEFAULT NULL,
	"alias" TEXT NULL DEFAULT NULL,
	"name_translation_id" BIGINT NULL DEFAULT NULL,
	"translation_id" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "fk_location_project_id_idx" ("project_id"),
	INDEX "location_deleted_idx" ("deleted"),
	CONSTRAINT "fk_location_project_id" FOREIGN KEY ("project_id") REFERENCES "public"."project" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.media
CREATE TABLE IF NOT EXISTS "media" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''media_reference_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"type" TEXT NULL DEFAULT NULL,
	"description" TEXT NULL DEFAULT NULL,
	"image" BYTEA NULL DEFAULT NULL,
	"pdf" BYTEA NULL DEFAULT NULL,
	"title_translation_id" INTEGER NULL DEFAULT NULL,
	"description_translation_id" INTEGER NULL DEFAULT NULL,
	"image_filename_front" TEXT NULL DEFAULT NULL,
	"image_filename_back" TEXT NULL DEFAULT NULL,
	"media_collection_id" BIGINT NULL DEFAULT NULL,
	"orig_date_year" INTEGER NULL DEFAULT NULL,
	"orig_date" DATE NULL DEFAULT NULL,
	"art_technique_translation_id" BIGINT NULL DEFAULT NULL,
	"sort_order" BIGINT NULL DEFAULT NULL,
	"sub_group" BIGINT NULL DEFAULT NULL,
	"external_reference" TEXT NULL DEFAULT NULL,
	"internal_reference" TEXT NULL DEFAULT NULL,
	"art_location" TEXT NULL DEFAULT NULL,
	"legacy_id" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id")
);



-- Dumping structure for table public.media_collection
CREATE TABLE IF NOT EXISTS "media_collection" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''media_collection_reference_seq''::regclass)',
	"title_translation_id" BIGINT NULL DEFAULT NULL,
	"description_translation_id" BIGINT NULL DEFAULT NULL,
	"project_id" BIGINT NULL DEFAULT NULL,
	"image_path" VARCHAR(512) NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"sort_order" SMALLINT NULL DEFAULT NULL,
	PRIMARY KEY ("id")
);



-- Dumping structure for table public.media_connection
CREATE TABLE IF NOT EXISTS "media_connection" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''event_connection_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"subject_id" BIGINT NULL DEFAULT NULL,
	"tag_id" BIGINT NULL DEFAULT NULL,
	"location_id" BIGINT NULL DEFAULT NULL,
	"event_id" BIGINT NULL DEFAULT NULL,
	"work_manifestation_id" BIGINT NULL DEFAULT NULL,
	"correspondence_id" BIGINT NULL DEFAULT NULL,
	"type" TEXT NULL DEFAULT NULL,
	"media_id" BIGINT NOT NULL,
	PRIMARY KEY ("id"),
	CONSTRAINT "media_id_fk" FOREIGN KEY ("media_id") REFERENCES "public"."media" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.project
CREATE TABLE IF NOT EXISTS "project" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''project_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"published" BIGINT NULL DEFAULT NULL,
	"name" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id")
);



-- Dumping structure for table public.publication
CREATE TABLE IF NOT EXISTS "publication" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''publication_seq''::regclass)',
	"publication_collection_id" BIGINT NULL DEFAULT NULL,
	"publication_comment_id" BIGINT NULL DEFAULT NULL,
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"date_published_externally" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"published" BIGINT NULL DEFAULT NULL,
	"legacy_id" TEXT NULL DEFAULT NULL,
	"published_by" TEXT NULL DEFAULT NULL,
	"original_filename" TEXT NULL DEFAULT NULL,
	"name" TEXT NULL DEFAULT NULL,
	"genre" TEXT NULL DEFAULT NULL,
	"publication_group_id" BIGINT NULL DEFAULT NULL,
	"original_publication_date" TEXT NULL DEFAULT NULL,
	"zts_id" BIGINT NULL DEFAULT NULL,
	"original_language" TEXT NULL DEFAULT NULL,
	"archive_signum" TEXT NULL DEFAULT NULL,
	"translation_id" BIGINT NULL DEFAULT NULL,
	"subtitle" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "fk_publication_publication_collection_id_idx" ("publication_collection_id"),
	INDEX "fk_publication_publication_comment_id_idx" ("publication_comment_id"),
	INDEX "fk_publication_publication_group_id_idx" ("publication_group_id"),
	CONSTRAINT "FK_publication_translation" FOREIGN KEY ("translation_id") REFERENCES "public"."translation" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_publication_publication_collection_id" FOREIGN KEY ("publication_collection_id") REFERENCES "public"."publication_collection" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_publication_publication_comment_id" FOREIGN KEY ("publication_comment_id") REFERENCES "public"."publication_comment" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_publication_publication_group_id" FOREIGN KEY ("publication_group_id") REFERENCES "public"."publication_group" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.publication_collection
CREATE TABLE IF NOT EXISTS "publication_collection" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''publication_collection_seq''::regclass)',
	"publication_collection_introduction_id" BIGINT NULL DEFAULT NULL,
	"publication_collection_title_id" BIGINT NULL DEFAULT NULL,
	"project_id" BIGINT NULL DEFAULT NULL,
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"date_published_externally" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"published" BIGINT NULL DEFAULT NULL,
	"name" TEXT NULL DEFAULT NULL,
	"legacy_id" TEXT NULL DEFAULT NULL,
	"translation_id" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "fk_publication_collection_project_id_idx" ("project_id"),
	INDEX "fk_publication_collection_publication_collection_intro_id_idx" ("publication_collection_introduction_id"),
	INDEX "fk_publication_collection_publication_collection_title_id_idx" ("publication_collection_title_id"),
	CONSTRAINT "FK_publication_collection_translation" FOREIGN KEY ("translation_id") REFERENCES "public"."translation" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_publication_collection_project_id" FOREIGN KEY ("project_id") REFERENCES "public"."project" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_publication_collection_publication_collection_intro_id" FOREIGN KEY ("publication_collection_introduction_id") REFERENCES "public"."publication_collection_introduction" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_publication_collection_publication_collection_title_id" FOREIGN KEY ("publication_collection_title_id") REFERENCES "public"."publication_collection_title" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.publication_collection_introduction
CREATE TABLE IF NOT EXISTS "publication_collection_introduction" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''publication_collection_intro_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT '2018-10-12 09:12:27.410734',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"date_published_externally" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"published" BIGINT NULL DEFAULT NULL,
	"legacy_id" TEXT NULL DEFAULT NULL,
	"original_filename" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id")
);



-- Dumping structure for table public.publication_collection_title
CREATE TABLE IF NOT EXISTS "publication_collection_title" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''publication_collection_title_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT '2018-10-12 09:12:27.501043',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"date_published_externally" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"published" BIGINT NULL DEFAULT NULL,
	"legacy_id" TEXT NULL DEFAULT NULL,
	"original_filename" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id")
);



-- Dumping structure for table public.publication_comment
CREATE TABLE IF NOT EXISTS "publication_comment" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''publication_comment_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"date_published_externally" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"published" BIGINT NULL DEFAULT NULL,
	"legacy_id" TEXT NULL DEFAULT NULL,
	"published_by" TEXT NULL DEFAULT NULL,
	"original_filename" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id")
);



-- Dumping structure for table public.publication_facsimile
CREATE TABLE IF NOT EXISTS "publication_facsimile" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''publication_facsimile_seq''::regclass)',
	"publication_facsimile_collection_id" BIGINT NULL DEFAULT NULL,
	"publication_id" BIGINT NULL DEFAULT NULL,
	"publication_manuscript_id" BIGINT NULL DEFAULT NULL,
	"publication_version_id" BIGINT NULL DEFAULT NULL,
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"page_nr" INTEGER NOT NULL,
	"section_id" BIGINT NOT NULL,
	"priority" BIGINT NOT NULL,
	"type" BIGINT NOT NULL,
	PRIMARY KEY ("id"),
	INDEX "facs_id" ("publication_facsimile_collection_id"),
	INDEX "fk_publication_facsimile_publication_id_idx" ("publication_id"),
	INDEX "fk_publication_facsimile_publication_manuscript_id_idx" ("publication_manuscript_id"),
	INDEX "fk_publication_facsimile_publication_version_id_idx" ("publication_version_id"),
	CONSTRAINT "fk_publication_facsimile_publication_facsimile_collection_id" FOREIGN KEY ("publication_facsimile_collection_id") REFERENCES "public"."publication_facsimile_collection" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_publication_facsimile_publication_id" FOREIGN KEY ("publication_id") REFERENCES "public"."publication" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_publication_facsimile_publication_manuscript_id" FOREIGN KEY ("publication_manuscript_id") REFERENCES "public"."publication_manuscript" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_publication_facsimile_publication_version_id" FOREIGN KEY ("publication_version_id") REFERENCES "public"."publication_version" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.publication_facsimile_collection
CREATE TABLE IF NOT EXISTS "publication_facsimile_collection" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''publication_facsimile_collec_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"title" TEXT NULL DEFAULT NULL,
	"number_of_pages" BIGINT NULL DEFAULT NULL,
	"start_page_number" BIGINT NULL DEFAULT NULL,
	"description" TEXT NULL DEFAULT NULL,
	"folder_path" TEXT NULL DEFAULT NULL,
	"page_comment" TEXT NULL DEFAULT NULL,
	"external_url" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id")
);



-- Dumping structure for table public.publication_facsimile_zone
CREATE TABLE IF NOT EXISTS "publication_facsimile_zone" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''publication_facsimile_zone_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT '2018-10-12 09:12:28.758617',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"publication_facsimile_id" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "fk_publication_facsimile_zone_publication_facsimile_id_idx" ("publication_facsimile_id"),
	CONSTRAINT "fk_publication_facsimile_zone_publication_facsimile_id" FOREIGN KEY ("publication_facsimile_id") REFERENCES "public"."publication_facsimile" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.publication_group
CREATE TABLE IF NOT EXISTS "publication_group" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''publication_group_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT '2018-10-12 09:12:27.977918',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"published" SMALLINT NULL DEFAULT '0',
	"name" TEXT NULL DEFAULT NULL,
	"translation_id" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	CONSTRAINT "FK_publication_group_translation" FOREIGN KEY ("translation_id") REFERENCES "public"."translation" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.publication_manuscript
CREATE TABLE IF NOT EXISTS "publication_manuscript" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''publication_manuscript_seq''::regclass)',
	"publication_id" BIGINT NULL DEFAULT NULL,
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"date_published_externally" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"published" BIGINT NULL DEFAULT NULL,
	"legacy_id" TEXT NULL DEFAULT NULL,
	"published_by" TEXT NULL DEFAULT NULL,
	"original_filename" TEXT NULL DEFAULT NULL,
	"name" TEXT NULL DEFAULT NULL,
	"type" BIGINT NULL DEFAULT NULL,
	"section_id" BIGINT NULL DEFAULT NULL,
	"sort_order" BIGINT NULL DEFAULT NULL,
	"archive_signum" TEXT NULL DEFAULT NULL,
	"original_language" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "fk_publication_manuscript_publication_id_idx" ("publication_id"),
	CONSTRAINT "fk_publication_manuscript_publication_id" FOREIGN KEY ("publication_id") REFERENCES "public"."publication" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.publication_song
CREATE TABLE IF NOT EXISTS "publication_song" (
	"id" INTEGER NOT NULL DEFAULT 'nextval(''publication_song_id_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'CURRENT_TIMESTAMP',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"publication_id" BIGINT NULL DEFAULT NULL,
	"original_id" TEXT NULL DEFAULT NULL,
	"name" TEXT NULL DEFAULT NULL,
	"type" TEXT NULL DEFAULT NULL,
	"number" TEXT NULL DEFAULT NULL,
	"variant" TEXT NULL DEFAULT NULL,
	"landscape" TEXT NULL DEFAULT NULL,
	"place" TEXT NULL DEFAULT NULL,
	"recorder_firstname" TEXT NULL DEFAULT NULL,
	"recorder_lastname" TEXT NULL DEFAULT NULL,
	"recorder_born_name" TEXT NULL DEFAULT NULL,
	"performer_firstname" TEXT NULL DEFAULT NULL,
	"performer_lastname" TEXT NULL DEFAULT NULL,
	"performer_born_name" TEXT NULL DEFAULT NULL,
	"note" TEXT NULL DEFAULT NULL,
	"comment" TEXT NULL DEFAULT NULL,
	"lyrics" TEXT NULL DEFAULT NULL,
	"original_collection_location" TEXT NULL DEFAULT NULL,
	"original_collection_signature" TEXT NULL DEFAULT NULL,
	"original_publication_date" TEXT NULL DEFAULT NULL,
	"page_number" TEXT NULL DEFAULT NULL,
	"subtype" TEXT NULL DEFAULT NULL,
	"volume" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	CONSTRAINT "fk_publication_song_publication_id" FOREIGN KEY ("publication_id") REFERENCES "public"."publication" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.publication_version
CREATE TABLE IF NOT EXISTS "publication_version" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''publication_version_seq''::regclass)',
	"publication_id" BIGINT NULL DEFAULT NULL,
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"date_published_externally" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"published" BIGINT NULL DEFAULT NULL,
	"legacy_id" TEXT NULL DEFAULT NULL,
	"published_by" TEXT NULL DEFAULT NULL,
	"original_filename" TEXT NULL DEFAULT NULL,
	"name" TEXT NULL DEFAULT NULL,
	"type" INTEGER NULL DEFAULT NULL,
	"section_id" INTEGER NULL DEFAULT NULL,
	"sort_order" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "fk_publication_version_publication_id_idx" ("publication_id"),
	CONSTRAINT "fk_publication_version_publication_id" FOREIGN KEY ("publication_id") REFERENCES "public"."publication" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.review_comment
CREATE TABLE IF NOT EXISTS "review_comment" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''review_comment_seq''::regclass)',
	"publication_id" BIGINT NULL DEFAULT NULL,
	"date_created" TIMESTAMP NULL DEFAULT '2018-10-12 09:12:28.800318',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"comment" TEXT NULL DEFAULT NULL,
	"user" TEXT NULL DEFAULT NULL,
	"legacy_id" TEXT NULL DEFAULT NULL,
	"review_comment_id" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "fk_review_comment_publication_id_idx" ("publication_id"),
	INDEX "fk_review_comment_review_comment_id_idx" ("review_comment_id"),
	CONSTRAINT "fk_review_comment_publication_id" FOREIGN KEY ("publication_id") REFERENCES "public"."publication" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_review_comment_review_comment_id" FOREIGN KEY ("review_comment_id") REFERENCES "public"."review_comment" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.subject
CREATE TABLE IF NOT EXISTS "subject" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''subject_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"type" TEXT NULL DEFAULT NULL,
	"first_name" TEXT NULL DEFAULT NULL,
	"last_name" TEXT NULL DEFAULT NULL,
	"place_of_birth" TEXT NULL DEFAULT NULL,
	"occupation" TEXT NULL DEFAULT NULL,
	"preposition" TEXT NULL DEFAULT NULL,
	"full_name" TEXT NULL DEFAULT NULL,
	"description" TEXT NULL DEFAULT NULL,
	"legacy_id" TEXT NULL DEFAULT NULL,
	"date_born" VARCHAR(30) NULL DEFAULT NULL,
	"date_deceased" VARCHAR(30) NULL DEFAULT NULL,
	"project_id" BIGINT NULL DEFAULT NULL,
	"source" TEXT NULL DEFAULT NULL,
	"alias" TEXT NULL DEFAULT NULL,
	"previous_last_name" TEXT NULL DEFAULT NULL,
	"alternative_form" TEXT NULL DEFAULT NULL,
	"translation_id" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "fk_subject_project_id_idx" ("project_id"),
	INDEX "subject_deleted_idx" ("deleted"),
	CONSTRAINT "FK_subject_translation" FOREIGN KEY ("translation_id") REFERENCES "public"."translation" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_subject_project_id" FOREIGN KEY ("project_id") REFERENCES "public"."project" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.tag
CREATE TABLE IF NOT EXISTS "tag" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''tag_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"type" TEXT NULL DEFAULT NULL,
	"name" TEXT NULL DEFAULT NULL,
	"description" TEXT NULL DEFAULT NULL,
	"legacy_id" TEXT NULL DEFAULT NULL,
	"project_id" BIGINT NULL DEFAULT NULL,
	"source" TEXT NULL DEFAULT NULL,
	"name_translation_id" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "fk_tag_project_id_idx" ("project_id"),
	INDEX "tag_deleted_idx" ("deleted"),
	CONSTRAINT "fk_tag_project_id" FOREIGN KEY ("project_id") REFERENCES "public"."project" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.translation
CREATE TABLE IF NOT EXISTS "translation" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''translation_id_seq''::regclass)',
	"neutral_text" TEXT NULL DEFAULT NULL,
	"finonto" INTEGER NULL DEFAULT NULL,
	PRIMARY KEY ("id")
);



-- Dumping structure for table public.translation_text
CREATE TABLE IF NOT EXISTS "translation_text" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''translation_text_id_seq''::regclass)',
	"translation_id" BIGINT NULL DEFAULT NULL,
	"language" VARCHAR(10) NULL DEFAULT NULL,
	"text" TEXT NULL DEFAULT NULL,
	"field_name" VARCHAR(200) NULL DEFAULT 'NULL::character varying',
	"table_name" VARCHAR(200) NULL DEFAULT 'NULL::character varying',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	PRIMARY KEY ("id"),
	CONSTRAINT "FK_translation_text_translation" FOREIGN KEY ("translation_id") REFERENCES "public"."translation" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.urn_lookup
CREATE TABLE IF NOT EXISTS "urn_lookup" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''urn_lookup_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT '2018-10-12 09:12:28.862527',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"urn" TEXT NULL DEFAULT NULL,
	"url" TEXT NULL DEFAULT NULL,
	"reference_text" TEXT NULL DEFAULT NULL,
	"intro_reference_text" TEXT NULL DEFAULT NULL,
	"project_id" BIGINT NULL DEFAULT NULL,
	"legacy_id" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "fk_urn_project_id_idx" ("project_id"),
	CONSTRAINT "fk_urn_project_id" FOREIGN KEY ("project_id") REFERENCES "public"."project" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.users
CREATE TABLE IF NOT EXISTS "users" (
	"ident" INTEGER NOT NULL DEFAULT 'nextval(''users_ident_seq''::regclass)',
	"email" VARCHAR(255) NOT NULL,
	"password" TEXT NOT NULL,
	"projects" TEXT NULL DEFAULT NULL,
	UNIQUE INDEX "users_email_key" ("email"),
	PRIMARY KEY ("ident")
);



-- Dumping structure for table public.work
CREATE TABLE IF NOT EXISTS "work" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''work_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"title" TEXT NULL DEFAULT NULL,
	"description" TEXT NULL DEFAULT NULL,
	"source" TEXT NULL DEFAULT NULL,
	"work_collection_id" BIGINT NULL DEFAULT NULL,
	"legacy_id" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "fk_work_work_collection_id_idx" ("work_collection_id"),
	INDEX "work_deleted_idx" ("deleted"),
	CONSTRAINT "fk_work_work_collection_id" FOREIGN KEY ("work_collection_id") REFERENCES "public"."work_collection" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.work_collection
CREATE TABLE IF NOT EXISTS "work_collection" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''work_collection_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"title" TEXT NULL DEFAULT NULL,
	"description" TEXT NULL DEFAULT NULL,
	"source" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "work_collection_deleted_idx" ("deleted")
);



-- Dumping structure for table public.work_manifestation
CREATE TABLE IF NOT EXISTS "work_manifestation" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''work_manifestation_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"title" TEXT NULL DEFAULT NULL,
	"type" TEXT NULL DEFAULT NULL,
	"description" TEXT NULL DEFAULT NULL,
	"source" TEXT NULL DEFAULT NULL,
	"linked_work_manifestation_id" BIGINT NULL DEFAULT NULL,
	"work_id" BIGINT NULL DEFAULT NULL,
	"work_manuscript_id" BIGINT NULL DEFAULT NULL,
	"translated_by" TEXT NULL DEFAULT NULL,
	"journal" TEXT NULL DEFAULT NULL,
	"publication_location" TEXT NULL DEFAULT NULL,
	"publisher" TEXT NULL DEFAULT NULL,
	"published_year" TEXT NULL DEFAULT NULL,
	"volume" TEXT NULL DEFAULT NULL,
	"total_pages" BIGINT NULL DEFAULT NULL,
	"ISBN" TEXT NULL DEFAULT NULL,
	"legacy_id" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "fk_manifestation_manuscript_id_idx" ("work_manuscript_id"),
	INDEX "fk_manifestation_work_id_idx" ("work_id"),
	INDEX "manifestation_deleted_idx" ("deleted"),
	CONSTRAINT "fk_manifestation_manuscript_id" FOREIGN KEY ("work_manuscript_id") REFERENCES "public"."work_manuscript" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_manifestation_work_id" FOREIGN KEY ("work_id") REFERENCES "public"."work" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for table public.work_manuscript
CREATE TABLE IF NOT EXISTS "work_manuscript" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''work_manuscript_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"title" TEXT NULL DEFAULT NULL,
	"referenced_as" TEXT NULL DEFAULT NULL,
	"description" TEXT NULL DEFAULT NULL,
	"source" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "manuscript_deleted_idx" ("deleted")
);



-- Dumping structure for table public.work_reference
CREATE TABLE IF NOT EXISTS "work_reference" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''work_reference_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT 'now()',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"referenced_as" TEXT NULL DEFAULT NULL,
	"reference" TEXT NULL DEFAULT NULL,
	"referenced_pages" TEXT NULL DEFAULT NULL,
	"source" TEXT NULL DEFAULT NULL,
	"project_id" BIGINT NULL DEFAULT NULL,
	"work_manifestation_id" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	INDEX "fk_work_reference_manifestation_id_idx" ("work_manifestation_id"),
	INDEX "fk_work_reference_project_id_idx" ("project_id"),
	INDEX "work_reference_deleted_idx" ("deleted"),
	CONSTRAINT "fk_work_reference_project_id" FOREIGN KEY ("project_id") REFERENCES "public"."project" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_work_reference_work_manifestation_id" FOREIGN KEY ("work_manifestation_id") REFERENCES "public"."work_manifestation" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);



-- Dumping structure for view public.get_manifestations_with_authors
DROP TABLE IF EXISTS "get_manifestations_with_authors";
CREATE VIEW "get_manifestations_with_authors" AS  SELECT row_to_json(t.*) AS json_data,
    t.project_id
   FROM ( SELECT w_m.id,
            w_m.date_created,
            w_m.date_modified,
            w_m.deleted,
            w_m.title,
            w_m.type,
            w_m.description,
            w_m.source,
            w_m.linked_work_manifestation_id,
            w_m.work_id,
            w_m.work_manuscript_id,
            w_m.translated_by,
            w_m.journal,
            w_m.publication_location,
            w_m.publisher,
            w_m.published_year,
            w_m.volume,
            w_m.total_pages,
            w_m."ISBN",
            w_r.project_id,
            w_r.reference,
            ( SELECT array_to_json(array_agg(row_to_json(d.*))) AS array_to_json
                   FROM ( SELECT s.id,
                            s.date_created,
                            s.date_modified,
                            s.deleted,
                            s.type,
                            s.first_name,
                            s.last_name,
                            s.place_of_birth,
                            s.occupation,
                            s.preposition,
                            s.full_name,
                            s.description,
                            s.legacy_id,
                            s.date_born,
                            s.date_deceased,
                            s.project_id,
                            s.source,
                            s.alias,
                            s.previous_last_name
                           FROM (event_connection ec
                             JOIN subject s ON ((s.id = ec.subject_id)))
                          WHERE ((ec.deleted = 0) AND (ec.work_manifestation_id = w_m.id))) d) AS authors
           FROM (work_manifestation w_m
             JOIN work_reference w_r ON ((w_r.work_manifestation_id = w_m.id)))
          WHERE ((w_r.deleted = 0) AND (w_m.deleted = 0))
          ORDER BY w_m.title) t;;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
