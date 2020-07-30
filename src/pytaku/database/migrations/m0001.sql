PRAGMA journal_mode=WAL;

create table user (
    id integer primary key,
    username text unique,
    password text
);

create table token (
    user_id integer,
    content text
);
