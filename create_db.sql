-- create all the spatial extension in pgsql.
CREATE EXTENSION postgis;
CREATE EXTENSION pgrouting;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION fuzzystrmatch;
CREATE EXTENSION postgis_tiger_geocoder;
CREATE EXTENSION address_standardizer;
-- verifying that all the extensions have been activated.
SELECT postgis_full_version();

-- 1.create the basic template for all the elements in this db.
CREATE SCHEMA templates

    CREATE TABLE templates.basic_template
    (
        uid      text                     NOT NULL
            CONSTRAINT basic_template_primary_key PRIMARY KEY,
        datetime timestamp WITH TIME ZONE NOT NULL
    );
COMMENT ON COLUMN templates.basic_template.datetime IS 'data updated time';
CREATE INDEX basic_template_time_index ON templates.basic_template (datetime DESC);

-- 2.create entity_template for spatial elements.
CREATE TABLE templates.entity_template
(
    adcode char(6) NOT NULL
)
    INHERITS (templates.basic_template);
COMMENT ON COLUMN templates.entity_template.adcode IS 'refer to the administration code where this entity located in';

CREATE INDEX entity_template_time_index ON templates.entity_template (datetime DESC);
CREATE INDEX entity_template_adcode_index ON templates.entity_template (adcode);

-- 3.create table to store boundaries.
CREATE SCHEMA boundary;

CREATE TABLE boundary.province
(
    name     text NOT NULL,
    geometry geometry(MultiPolygon, 4326),
    CONSTRAINT province_primary_key PRIMARY KEY (uid),
    CONSTRAINT province_adcode_key UNIQUE (adcode)
)
    INHERITS (templates.entity_template);

CREATE INDEX province_adcode_index ON boundary.province (adcode);
CREATE INDEX province_time_index ON boundary.province (datetime DESC);
CREATE INDEX province_geometry_index ON boundary.province USING gist (geometry);

CREATE TABLE boundary.city
(
    name            text    NOT NULL,
    province_adcode char(6) NOT NULL
        CONSTRAINT city_province_foreign_key REFERENCES boundary.province (adcode),
    geometry        geometry(MultiPolygon, 4326),
    CONSTRAINT city_primary_key PRIMARY KEY (uid),
    CONSTRAINT city_adcode_key UNIQUE (adcode)
)
    INHERITS (templates.entity_template);
CREATE INDEX city_adcode_index ON boundary.city (adcode);
CREATE INDEX city_time_index ON boundary.city (datetime);
CREATE INDEX city_geometry_index ON boundary.city USING gist (geometry);

-- 4. create



