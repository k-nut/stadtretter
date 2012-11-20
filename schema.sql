drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  name string not null,
  title string not null,
  picture string not null,
  lat float not null,
  lon float not null,
  pubdate date not null
  );
