#create database country_co2;
use country_co2;
drop table if exists map_country_iso,co2_emission,co2_rank;

#create mapping table for country name and ISO code
create table map_country_iso(
	id int auto_increment primary key,
    country varchar(255) not null unique,
    iso_code varchar(50) not null unique);

#create the co2 emission table, making the primary key the combination
#of year and ISO code
create table co2_emission(
	iso_code varchar(50) not null,
    year int not null,
    co2_emission mediumint,
    primary key (iso_code,year));
    
#create the co2 emisison rank for each country
create table co2_rank(
	iso_code varchar(50) not null,
    year int not null,
    rank int,
    primary key (iso_code,year));
    


