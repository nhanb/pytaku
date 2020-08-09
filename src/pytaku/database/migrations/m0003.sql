-- Dropping the unique(id, site) constraint.
-- SQLite doesn't let you do that directly so gotta create a new table
-- then copy existing data over.

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
    updated_at text default (datetime('now')), is_webtoon boolean,

    foreign key (title_id, site) references title (id, site),
    unique(site, title_id, id),
    unique(site, title_id, num_major, num_minor)
);

insert into chapter select * from old_chapter;
