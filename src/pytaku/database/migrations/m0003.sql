-- Dropping the unique(id, site) constraint.
-- SQLite doesn't let you do that directly so gotta create a new table
-- then copy existing data over.

-- To future self, before doing anything similar in the future, please,
-- _please_ read sqlite's documentation on the matter and follow the laid out
-- steps, otherwise you'll be in a world of hurt:
-- https://www.sqlite.org/lang_altertable.html#making_other_kinds_of_table_schema_changes

pragma foreign_keys = off; -- to let us do anything at all
begin transaction;

-- First, handle `chapter` table
create table new_chapter (
    id text,
    title_id text,
    site text,
    num_major integer,
    num_minor integer,
    name text,
    pages text,
    groups text,
    updated_at text default (datetime('now')),
    is_webtoon boolean,

    foreign key (title_id, site) references title (id, site),
    unique(site, title_id, id),
    unique(site, title_id, num_major, num_minor)
);
insert into new_chapter select * from chapter;
drop table chapter;
alter table new_chapter rename to chapter;

-- `read` table needs a new "title_id" column too
create table new_read (
    user_id integer not null,
    site text not null,
    title_id text, -- nullable to accomodate existing mangadex rows, urgh.
    chapter_id text not null,
    updated_at text default (datetime('now')),

    foreign key (user_id) references user (id),
    foreign key (site, title_id, chapter_id) references chapter (site, title_id, id),
    unique(user_id, site, title_id, chapter_id)
);
insert into new_read (user_id, site, chapter_id, updated_at)
    select user_id, site, chapter_id, updated_at from read;
drop table read;
alter table new_read rename to read;

pragma foreign_key_check;
commit;
pragma foreign_keys = on;
