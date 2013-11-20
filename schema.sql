drop table if exists entries;
create table tags (
  id integer primary key autoincrement,
  epoch integer not null,
  time datetime not null,
  tag text not null
);
