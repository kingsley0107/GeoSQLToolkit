-- basic template for all the elements.
create schema templates

create table templates.basic_template
(
    uid       text                     not null
        constraint basic_template_pk
            primary key,
    date_time timestamp with time zone not null
);

comment on column templates.basic_template.date_time is 'data updated time';


create index basic_template_date_time_index
    on templates.basic_template (date_time desc);

-- entity template, eg. city, buildings, poi
create table templates.entity_template
(
    adcode char(6) not null
)
    inherits (templates.basic_template);

comment on column templates.entity_template.adcode is 'administration code';


create index entity_template_adcode_index
    on templates.entity_template (adcode);

create index entity_template_date_time_index
    on templates.entity_template (date_time);


-- administration boundary eg. cities, provinces...
create schema boundary;

create table boundary.province
(
    name     text not null,
    geometry geometry(MultiPolygon, 4326),
    constraint province_pk
        primary key (uid),
    constraint province_adcodek
        unique (adcode)
)
    inherits (templates.entity_template);

comment on table boundary.province is 'boundary of province';


create index province_adcode_index
    on boundary.province (adcode);

create index province_date_time_index
    on boundary.province (date_time);

create index province_geometry_index
    on boundary.province using gist (geometry);

create table boundary.city
(
    province_adcode char(6) not null
        constraint city_province_null_fk
            references boundary.province (adcode),
    name            text    not null,
    geometry        geometry(MultiPolygon, 4326),
    constraint city_pk
        primary key (uid),
    constraint city_adcodek
        unique (adcode)
)
    inherits (templates.entity_template);
-- inhertis: adcode from entity_template.
comment on table boundary.city is 'boundary of cities';


create index city_adcode_index
    on boundary.city (adcode);

create index city_date_time_index
    on boundary.city (date_time);

create index city_geometry_index
    on boundary.city using gist (geometry);



create schema building;

create table building.building
(
    city_uid     text
        constraint building_city_null_fk
            references boundary.city,
    height        integer,
    function_type text,
    sub_type      char(6),
    level         integer,
    geometry      geometry(Polygon, 4326),
    constraint building_pk
        primary key (uid)
)
    inherits (templates.entity_template);

comment on table building.building is 'building in city';

comment on column building.building.function_type is 'the function of city,eg. residential, commercial...';

comment on column building.building.sub_type is 'sub typecode';

comment on column building.building.level is 'floor';


create index building_adcode_index
    on building.building (adcode);

create index building_date_time_index
    on building.building (date_time);



create schema grid;

create table grid.grid_200
(

    geometry          geometry(Polygon, 4326),
    constraint grid_200_pk
        primary key (uid)
)
    inherits (templates.entity_template);


create index grid_200_adcode_index
    on grid.grid_200 (adcode);

create index grid_200_date_time_index
    on grid.grid_200 (date_time);

create index grid_200_geometry_index
    on grid.grid_200 using gist (geometry);


create schema road;

create table road.road
(
    name     text,
    geometry geometry(MultiLineString, 4326),
    constraint road_pk
        primary key (uid)
)
    inherits (templates.entity_template);


create index road_adcode_index
    on road.road (adcode);

create index road_date_time_index
    on road.road (date_time);

create index road_geometry_index
    on road.road using gist (geometry);

create schema land_transaction;

create table land_transaction.land
(
    city_uid text not null
        constraint land_city_null_fk
            references boundary.city,
    geometry geometry(Point, 4326),
    constraint land_pk
        primary key (uid)
)
    inherits (templates.entity_template);

comment on table land_transaction.land is 'transaction on land';

create index land_adcode_index
    on land_transaction.land (adcode);

create index land_date_time_index
    on land_transaction.land (date_time);

create index land_geometry_index
    on land_transaction.land using gist (geometry);


create table land_transaction.lj_resi_rent
(
    city_uid     text
        constraint lj_resi_rent_aoi_null_fk
            references boundary.city,
    unit_rent   real not null,
    xiaoqu_name text not null,
    hid         text,
    area        real,
    total_rent  real,
    layout      text,
    direction   text,
    bizcircle   text,
    description text,
    geometry    geometry(Point, 4326),
    constraint lj_resi_rent_pk
        primary key (uid)
)
    inherits (templates.entity_template);

comment on table land_transaction.lj_resi_rent is 'transaction on lianjia';


create index lj_resi_rent_adcode_index
    on land_transaction.lj_resi_rent (adcode);

create index lj_resi_rent_date_time_index
    on land_transaction.lj_resi_rent (date_time);

create index lj_resi_rent_geometry_index
    on land_transaction.lj_resi_rent using gist (geometry);




create table land_transaction.lj_second_resi_sale
(
    city_uid     text
        constraint lj_second_resi_sale_city_null_fk
            references boundary.city,
    unit_price  real not null,
    xiaoqu_name text not null,
    hid         text,
    area        real,
    total_price real,
    layout      text,
    direction   text,
    bizcircle   text,
    description text,
    fitment     text,
    geometry    geometry(Point, 4326),
    constraint lj_second_resi_sale_pk
        primary key (uid)
)
    inherits (templates.entity_template);

comment on table land_transaction.lj_second_resi_sale is 'sales for second-hand resi on liajia';

-- alter table transaction.lj_second_resi_sale
--     owner to data_platform_rw;

create index lj_second_resi_sale_adcode_index
    on land_transaction.lj_second_resi_sale (adcode);

create index lj_second_resi_sale_date_time_index
    on land_transaction.lj_second_resi_sale (date_time);

create index lj_second_resi_sale_geometry_index
    on land_transaction.lj_second_resi_sale using gist (geometry);


create schema transit;

create table transit.bus_line
(
    bd_uid         text not null,
    name           text not null,
    full_name      text,
    company        text,
    line_direction text,
    geometry       geometry(Point, 4326),
    constraint bus_line_pk
        primary key (uid)
)
    inherits (templates.entity_template);

comment on table transit.bus_line is '公交线 default source: baidu';

-- alter table transit.bus_line
--     owner to data_platform_rw;

create index bus_line_adcode_index
    on transit.bus_line (adcode);

create index bus_line_date_time_index
    on transit.bus_line (date_time);

create index bus_line_geometry_index
    on transit.bus_line using gist (geometry);

create table transit.bus_station
(
    bd_uid    text not null,
    name      text not null,
    line_name text,
    geometry  geometry(Point, 4326),
    constraint bus_station_pk
        primary key (uid)
)
    inherits (templates.entity_template);

comment on table transit.bus_station is '公交站';

-- alter table transit.bus_station
--     owner to data_platform_rw;

create index bus_station_adcode_index
    on transit.bus_station (adcode);

create index bus_station_date_time_index
    on transit.bus_station (date_time);

create index bus_station_geometry_index
    on transit.bus_station using gist (geometry);

create table transit.metro_line
(
    bd_uid         text not null,
    name           text not null,
    full_name      text,
    company        text,
    line_direction text,
    geometry       geometry(Point, 4326),
    constraint metro_line_pk
        primary key (uid)
)
    inherits (templates.entity_template);

comment on table transit.metro_line is '地铁线';

-- alter table transit.metro_line
--     owner to data_platform_rw;

create index metro_line_adcode_index
    on transit.metro_line (adcode);

create index metro_line_date_time_index
    on transit.metro_line (date_time);

create index metro_line_geometry_index
    on transit.metro_line using gist (geometry);

create table transit.metro_station
(
    bd_uid    text not null,
    name      text not null,
    line_name text,
    geometry  geometry(Point, 4326),
    constraint metro_station_pk
        primary key (uid)
)
    inherits (templates.entity_template);

comment on table transit.metro_station is '地铁站';

-- alter table transit.metro_station
--     owner to data_platform_rw;

create index metro_station_adcode_index
    on transit.metro_station (adcode);

create index metro_station_date_time_index
    on transit.metro_station (date_time);

create index metro_station_geometry_index
    on transit.metro_station using gist (geometry);

create table transit.metro_station_entrance
(
    metro_station_uid text not null
        constraint metro_station_entrance_metro_station_null_fk
            references transit.metro_station,
    name              text not null,
    geometry          geometry(Point, 4326),
    constraint metro_station_entrance_pk
        primary key (uid)
)
    inherits (templates.entity_template);

comment on table transit.metro_station_entrance is '地铁站出入口';

-- alter table transit.metro_station_entrance
--     owner to data_platform_rw;

create index metro_station_entrance_adcode_index
    on transit.metro_station_entrance (adcode);

create index metro_station_entrance_date_time_index
    on transit.metro_station_entrance (date_time);

create index metro_station_entrance_geometry_index
    on transit.metro_station_entrance using gist (geometry);



create schema poi;

create table poi.poi
(
    pid                  text,
    name                 text    not null,
    typecode             varchar not null,
    common_type          text,
    is_ground_floor_shop boolean,
    address              text,
    geometry             geometry(Point, 4326),
    constraint poi_pk
        primary key (uid)
)
    inherits (templates.entity_template);

comment on table poi.poi is 'default source: Amap';

comment on column poi.poi.typecode is 'https://lbs.amap.com/api/webservice/download';

comment on column poi.poi.common_type is '通用类别';

comment on column poi.poi.is_ground_floor_shop is '是底商';

-- alter table poi.poi
--     owner to data_platform_rw;

create index poi_adcode_index
    on poi.poi (adcode);

create index poi_date_time_index
    on poi.poi (date_time);

create index poi_geometry_index
    on poi.poi using gist (geometry);

create table poi.hospital
(
    poi_uid    text not null
        constraint hospital_poi_null_fk
            references poi.poi,
    aoi_uid    text
            ,
    name       text not null,
    level      text not null,
    insurance  boolean,
    nickname   text,
    character  text,
    built_year integer,
    address    text
)
    inherits (templates.basic_template);

comment on table poi.hospital is '医院 source: yingcai, https://www.healthr.com/';

comment on column poi.hospital.insurance is '是否医保';

comment on column poi.hospital.nickname is '别称';

comment on column poi.hospital.character is '公私 public or private';


create table grid.facility_accessibility
(
    grid_uid text not null
        constraint facility_accessibility_grid_200_null_fk
            references grid.grid_200
)
    inherits (templates.basic_template);



create table grid.house_price
(
    grid_uid text not null
        constraint house_price_grid_200_null_fk
            references grid.grid_200
)
    inherits (templates.basic_template);

-- alter table grid.house_price
--     owner to data_platform_rw;

create table grid.transit
(
    grid_uid text not null
        constraint transit_grid_200_null_fk
            references grid.grid_200
)
    inherits (templates.basic_template);
