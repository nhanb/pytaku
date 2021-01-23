begin transaction;

alter table title add column descriptions_format text not null default 'text';

commit;
