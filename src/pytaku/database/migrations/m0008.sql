-- Move is_webtoon column from chapter to title.
-- No need to migrate existing data: scheduled title updates will populate the
-- correct data in no time.

pragma foreign_keys = off; -- to let us do anything at all
begin transaction;

-- Easy part: add is_webtoon column to "title" table
alter table title add column is_webtoon boolean not null default false;

-- Clumsy part: remove is_webtoon column from "chapter" table
---- 1. create new
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
    pages_alt text not null default '[]',
    foreign key (title_id, site) references title (id, site),
    unique(site, title_id, id)
);
---- 2. copy from old to new
insert into new_chapter (id, title_id, site, num_major, num_minor, name,
                         pages, groups, updated_at, pages_alt)
    select id, title_id, site, num_major, num_minor, name, pages, groups,
           updated_at, pages_alt
    from chapter;
---- 3. drop old
drop table chapter;
---- 4. rename new
alter table new_chapter rename to chapter;

pragma foreign_key_check;
commit;
pragma foreign_keys = on;
