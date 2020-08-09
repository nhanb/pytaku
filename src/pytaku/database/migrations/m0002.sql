create table keyval_store (
    key text primary key,
    value text not null,
    updated_at text default (datetime('now'))
);
