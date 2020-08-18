begin transaction;

create table token (
    user_id integer not null,
    token text unique not null,
    created_at text not null default (datetime('now')),
    last_accessed_at text not null default (datetime('now')),
    lifespan text not null, -- '+1 day', '+365 days', etc.

    foreign key (user_id) references user (id)
);

commit;
