-- --------------------------------------------------------
-- Host:                         
-- Server version:               PostgreSQL 10.23 on x86_64-pc-linux-gnu, compiled by Debian clang version 12.0.1, 64-bit
-- Server OS:                    
-- HeidiSQL Version:             11.3.0.6295
-- --------------------------------------------------------

-- Dumping structure for table public.contribution
CREATE TABLE IF NOT EXISTS "contribution" (
	"id" BIGINT NOT NULL DEFAULT 'nextval(''contribution_id_seq''::regclass)',
	"date_created" TIMESTAMP NULL DEFAULT '2022-03-29 11:17:32.243572',
	"date_modified" TIMESTAMP NULL DEFAULT NULL,
	"publication_collection_id" BIGINT NULL DEFAULT NULL,
	"publication_collection_introduction_id" BIGINT NULL DEFAULT NULL,
	"publication_collection_title_id" BIGINT NULL DEFAULT NULL,
	"publication_id" BIGINT NULL DEFAULT NULL,
	"publication_manuscript_id" BIGINT NULL DEFAULT NULL,
	"deleted" SMALLINT NULL DEFAULT '0',
	"type" TEXT NULL DEFAULT NULL,
	"text_language" TEXT NULL DEFAULT NULL,
	"contributor_id" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	CONSTRAINT "FK_contribution_contributor" FOREIGN KEY ("contributor_id") REFERENCES "public"."contributor" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "FK_contribution_publication" FOREIGN KEY ("publication_id") REFERENCES "public"."publication" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "FK_contribution_publication_collection" FOREIGN KEY ("publication_collection_id") REFERENCES "public"."publication_collection" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "FK_contribution_publication_collection_introduction" FOREIGN KEY ("publication_collection_introduction_id") REFERENCES "public"."publication_collection_introduction" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "FK_contribution_publication_collection_title" FOREIGN KEY ("publication_collection_title_id") REFERENCES "public"."publication_collection_title" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "FK_contribution_publication_manuscript" FOREIGN KEY ("publication_manuscript_id") REFERENCES "public"."publication_manuscript" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);

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
	CONSTRAINT "fk_publication_publication_collection_id" FOREIGN KEY ("publication_collection_id") REFERENCES "public"."publication_collection" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_publication_publication_comment_id" FOREIGN KEY ("publication_comment_id") REFERENCES "public"."publication_comment" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_publication_publication_group_id" FOREIGN KEY ("publication_group_id") REFERENCES "public"."publication_group" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "FK_publication_translation" FOREIGN KEY ("translation_id") REFERENCES "public"."translation" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
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
	CONSTRAINT "fk_publication_collection_project_id" FOREIGN KEY ("project_id") REFERENCES "public"."project" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_publication_collection_publication_collection_intro_id" FOREIGN KEY ("publication_collection_introduction_id") REFERENCES "public"."publication_collection_introduction" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "fk_publication_collection_publication_collection_title_id" FOREIGN KEY ("publication_collection_title_id") REFERENCES "public"."publication_collection_title" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "FK_publication_collection_translation" FOREIGN KEY ("translation_id") REFERENCES "public"."translation" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
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
	"translation_id" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	CONSTRAINT "FK_publication_collection_introduction_translation" FOREIGN KEY ("translation_id") REFERENCES "public"."translation" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
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
	"translation_id" BIGINT NULL DEFAULT NULL,
	PRIMARY KEY ("id"),
	CONSTRAINT "FK_publication_collection_title_translation" FOREIGN KEY ("translation_id") REFERENCES "public"."translation" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
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
	CONSTRAINT "fk_subject_project_id" FOREIGN KEY ("project_id") REFERENCES "public"."project" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT "FK_subject_translation" FOREIGN KEY ("translation_id") REFERENCES "public"."translation" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
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