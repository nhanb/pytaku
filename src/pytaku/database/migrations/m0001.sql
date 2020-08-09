begin transaction;

create table title (
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
    unique(id, title_id, site),
    unique(id, site),
    unique(num_major, num_minor, title_id)
);

create table user (
    id integer primary key,
    username text unique,
    password text,
    created_at text default (datetime('now'))
);

create table follow (
    user_id integer not null,
    title_id text not null,
    site text not null,
    created_at text default (datetime('now')),

    foreign key (title_id, site) references title (id, site),
    foreign key (user_id) references user (id),
    unique(user_id, title_id, site)
);

create table read (
    user_id integer not null,
    chapter_id text not null,
    site text not null,
    updated_at text default (datetime('now')),

    foreign key (user_id) references user (id),
    foreign key (chapter_id, site) references chapter (id, site),
    unique(user_id, chapter_id, site)
);

commit;
