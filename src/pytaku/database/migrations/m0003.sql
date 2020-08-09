-- Dropping the unique(id, site) constraint.
-- SQLite doesn't let you do that directly so gotta create a new table
-- then copy existing data over.

pragma foreign_keys = off; -- to let us do anything at all
pragma legacy_alter_table = on; -- prevent foreign keys from renaming to 'old_chapter' as well
begin transaction;

alter table chapter rename to old_chapter;
create table chapter (
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
insert into chapter select * from old_chapter;
drop table old_chapter;


-- "read" table needs a new "title_id" column too
alter table read rename to old_read;
create table read (
    user_id integer not null,
    site text not null,
    title_id text, -- nullable to accomodate existing mangadex rows, urgh.
    chapter_id text not null,
    updated_at text default (datetime('now')),

    foreign key (user_id) references user (id),
    foreign key (site, title_id, chapter_id) references chapter (site, title_id, id),
    unique(user_id, site, title_id, chapter_id)
);
insert into read (user_id, site, chapter_id, updated_at)
    select user_id, site, chapter_id, updated_at from old_read;
drop table old_read;

commit;
pragma foreign_keys = on;
pragma legacy_alter_table = off;
