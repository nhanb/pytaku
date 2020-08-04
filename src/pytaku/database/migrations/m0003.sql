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
