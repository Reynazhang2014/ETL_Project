#create database country_co2;
use national_footprint;
drop table if exists area,co2_emission_amt,co2_emission_rank,e_footprint,
map_iso_subregion,map_subregion_region,population;
drop table if exists map_iso_country;
;

#create mapping table for country name and ISO code
create table map_iso_country(
	iso_code varchar(50) not null unique,
    country varchar(255) not null unique);

create table area(
	Total_in_km2_mi2 varchar(200),
    Land_in_km2_mi2 varchar(200),
	Water_in_km2_mi2 varchar(200),
    water_pct text,
    Notes text,
    iso_code varchar(50) not null,
    primary key (iso_code));


#create the co2 emission table, making the primary key the combination
#of year and ISO code
create table co2_emission_amt(
	iso_code varchar(50) not null,
    year int not null,
    co2_emission text,
    primary key (iso_code,year));
    
#create the co2 emisison rank for each country
create table co2_emission_rank(
	iso_code varchar(50) not null,
    year int not null,
    rank int,
    primary key (iso_code,year));
    

create table e_footprint(
	iso_code varchar(50) not null,
    year int not null,
    record varchar(255),
    crop_land text,
    grazing_land text,
    forest_land text,
    fishing_ground text,
    built_up_land text,
    carbon text,
    primary key (iso_code, year, record));

create table map_iso_subregion(
	iso_code varchar(50) not null,
    UN_subregion varchar(255),
    primary key (iso_code));

create table map_subregion_region(
    UN_subregion varchar(255) not null,
    UN_region varchar(255),
    primary key (UN_subregion));

create table population(
	iso_code varchar(50) not null,
    year int not null,
    population bigint,
    primary key (iso_code,year));
    
    
##Then update the foreign keys for each table (if any)
# update co2_emission_amt's foreign key
ALTER TABLE `national_footprint`.`co2_emission_amt` 
ADD INDEX `fk_iso_code_idx` (`iso_code` ASC);
;

ALTER TABLE `national_footprint`.`co2_emission_amt` 
ADD CONSTRAINT `fk_iso_code`
  FOREIGN KEY (`iso_code`)
  REFERENCES `national_footprint`.`map_iso_country` (`iso_code`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


# update co2_emission_rank's foreign key
ALTER TABLE `national_footprint`.`co2_emission_rank` 
ADD CONSTRAINT `fk_iso_code1`
  FOREIGN KEY (`iso_code`)
  REFERENCES `national_footprint`.`map_iso_country` (`iso_code`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


# update e_footprint's foreign key
ALTER TABLE `national_footprint`.`e_footprint` 
ADD CONSTRAINT `fk_iso_code2`
  FOREIGN KEY (`iso_code`)
  REFERENCES `national_footprint`.`map_iso_country` (`iso_code`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

  
# update map_iso_subregion's foreign key
ALTER TABLE `national_footprint`.`map_iso_subregion` 
ADD CONSTRAINT `fk_iso_code3`
  FOREIGN KEY (`iso_code`)
  REFERENCES `national_footprint`.`map_iso_country` (`iso_code`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


# update population's foreign key
ALTER TABLE `national_footprint`.`population` 
ADD CONSTRAINT `fk_iso_code4`
  FOREIGN KEY (`iso_code`)
  REFERENCES `national_footprint`.`map_iso_country` (`iso_code`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;
  
# map_iso_subregion's subregion foreign key
ALTER TABLE `national_footprint`.`map_iso_subregion` 
ADD INDEX `fk_subregion_idx` (`UN_subregion` ASC);
;
ALTER TABLE `national_footprint`.`map_iso_subregion` 
ADD CONSTRAINT `fk_subregion`
  FOREIGN KEY (`UN_subregion`)
  REFERENCES `national_footprint`.`map_subregion_region` (`UN_subregion`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;

# update area's foreign key
ALTER TABLE `national_footprint`.`area` 
ADD CONSTRAINT `fk_iso_code5`
  FOREIGN KEY (`iso_code`)
  REFERENCES `national_footprint`.`map_iso_country` (`iso_code`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


    

