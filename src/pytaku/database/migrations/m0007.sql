-- Add alternative page urls as backup because mangadex is flaky.
begin transaction;

alter table chapter add column pages_alt text not null default '[]';

commit;
