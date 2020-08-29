-- Remove unique num_major, num_minor unique constraint.
-- Because mangadex can have the same chapter uploaded by different groups.

pragma foreign_keys = off; -- to let us do anything at all
begin transaction;

create table new_chapter(
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
    unique(site, title_id, id)
);
insert into new_chapter select * from chapter;
drop table chapter;
alter table new_chapter rename to chapter;

pragma foreign_key_check;
commit;
pragma foreign_keys = on;
