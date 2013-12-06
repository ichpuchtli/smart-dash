/* Dash DB */

/* Detected Tags including unregistered tags */
drop table if exists tags;
create table tags (
  id integer primary key autoincrement,
  epoch integer not null default (strftime('%s', 'now')),
  time timestamp not null default (datetime('now')),
  tag text not null
);

/* Settings Dictionary */
drop table if exists settings;
create table settings (
  id integer primary key autoincrement,
  key text not null,
  value text not null
);

/* Live RSSI values */
drop table if exists rssi;
create table rssi (
  id integer primary key autoincrement,
  epoch integer not null default (strftime('%s', 'now')),
  time timestamp not null default (datetime('now')),
  value integer not null
);

/* Tuning Data */
drop table if exists tuning;
create table tuning (
  id integer primary key autoincrement,
  value integer not null
);

/* Amplitude values */
drop table if exists amplitude;
create table amplitude (
  id integer primary key autoincrement,
  epoch integer not null default (strftime('%s', 'now')),
  time timestamp not null default (datetime('now')),
  value integer not null
);
