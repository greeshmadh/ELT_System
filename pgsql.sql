create database elt_db;

CREATE USER elt_user WITH PASSWORD 'elt_password';
GRANT ALL PRIVILEGES ON DATABASE elt_db TO elt_user;

elt_db;

CREATE TABLE raw_data (
    id Integer PRIMARY KEY,
    name TEXT,
    role TEXT
);

select * from raw_data;