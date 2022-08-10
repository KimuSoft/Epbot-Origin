create table rooms (
    name text default '',
    cleans integer not null,
    season integer not null,
    biome integer not null,
    facilities json,
    land_value integer,
    selling_now integer,
    fee integer,
    id varchar(20) not null primary key,
    exp integer not null default 0,
    owner varchar(20) not null
);
create table users (
    name text not null default '알 수 없는 유저',
    money integer not null default 0,
    exp integer not null default 0,
    fishing_now integer not null default 0,
    theme json not null default '[]'::json,
    dex json not null default '{}'::json,
    biggest_size integer,
    fish json not null default '[]'::json,
    id varchar(20) not null primary key,
    biggest_name text
);
create table fish (
    id integer primary key,
    name text unique,
    cost integer default 0,
    length integer default 0,
    seasons text default '1234',
    rarity text default '0',
    biomes text default '123',
    user_num integer default 0,
    historic integer default 0,
    room_level integer default 1,
    eng_name text
);
alter table rooms drop column selling_now;
alter table users drop column fishing_now;