drop table if exists tags;
create table tags (
  id integer primary key autoincrement,
  epoch integer not null,
  time timestamp not null default CURRENT_TIMESTAMP,
  tag text not null
);
