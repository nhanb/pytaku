create table title (
    id text,
    site text,
    chapters text,
    alt_names text,
    descriptions text,

    unique(id, site)
);

create table chapter (
    id text,
    title_id text,
    num_major integer,
    num_minor integer,
    name text,
    pages text,
    groups text,

    foreign key (title_id) references title (id),
    unique(id, title_id),
    unique(num_major, num_minor, title_id)
);
