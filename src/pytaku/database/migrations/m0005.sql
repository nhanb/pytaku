-- Remove foreign key from "read" table pointing to "chapter".
-- So we can, say, mark all chapters of a title as read even if some of those
-- chapters haven't been created.

pragma foreign_keys = off; -- to let us do anything at all
begin transaction;

create table new_read (
    user_id integer not null,
    site text not null,
    title_id text, -- nullable to accomodate existing mangadex rows, urgh.
    chapter_id text not null,
    updated_at text default (datetime('now')),

    foreign key (user_id) references user (id),
    unique(user_id, site, title_id, chapter_id)
);
insert into new_read select * from read;
drop table read;
alter table new_read rename to read;

pragma foreign_key_check;
commit;
pragma foreign_keys = on;
