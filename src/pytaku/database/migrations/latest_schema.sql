-- This file is auto-generated by the migration script
-- for reference purposes only. DO NOT EDIT.

CREATE TABLE title (
    id text,
    name text,
    site text,
    cover_ext text,
    chapters text,
    alt_names text,
    descriptions text,
    updated_at text default (datetime('now')),

    unique(id, site)
);
CREATE TABLE user (
    id integer primary key,
    username text unique,
    password text,
    created_at text default (datetime('now'))
);
CREATE TABLE follow (
    user_id integer not null,
    title_id text not null,
    site text not null,
    created_at text default (datetime('now')),

    foreign key (title_id, site) references title (id, site),
    foreign key (user_id) references user (id),
    unique(user_id, title_id, site)
);
CREATE TABLE keyval_store (
    key text primary key,
    value text not null,
    updated_at text default (datetime('now'))
);
CREATE TABLE chapter (
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
CREATE TABLE read (
    user_id integer not null,
    site text not null,
    title_id text, -- nullable to accomodate existing mangadex rows, urgh.
    chapter_id text not null,
    updated_at text default (datetime('now')),

    foreign key (user_id) references user (id),
    foreign key (site, title_id, chapter_id) references chapter (site, title_id, id),
    unique(user_id, site, title_id, chapter_id)
);
