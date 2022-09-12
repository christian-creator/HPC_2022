-- Create database
CREATE DATABASE s165476;
USE s165476;

-- Initialzing the person table 
CREATE TABLE person (
cpr CHAR(11),
first_name VARCHAR(100),
last_name VARCHAR(100),
height INT default NULL,
weight INT default NULL,
mother CHAR(11) default NULL,
father CHAR(11) default NULL,
PRIMARY KEY(cpr));

-- Initialzing the marriage table 
CREATE TABLE marriage (
male_cpr CHAR(11) DEFAULT NULL,
female_cpr CHAR(11) DEFAULT NULL,
start CHAR(8) DEFAULT NULL,
end CHAR(8) DEFAULT NULL,
PRIMARY KEY(male_cpr,female_cpr));

-- Initialzing the diseases table 
CREATE TABLE diseases (
cpr CHAR(11),
disease_name VARCHAR(100),
date CHAR(8));

-- Reading the CSV files into the tables
LOAD DATA LOCAL INFILE '/home/projects/pr_course/persons.csv' INTO TABLE person FIELDS TERMINATED BY ',';
LOAD DATA LOCAL INFILE '/home/projects/pr_course/marriage.csv' INTO TABLE marriage FIELDS TERMINATED BY ',';
LOAD DATA LOCAL INFILE '/home/projects/pr_course/disease.csv' INTO TABLE diseases FIELDS TERMINATED BY ',';

-- Show the warnings
SHOW WARNINGS

-- General functions
DELETE FROM person;
DROP TABLE marriage;
DROP TABLE person;

-- Who do not have a father?
select * FROM person WHERE father='';

-- How many do not have a mother?  
select COUNT(cpr) FROM person WHERE mother='';

-- How many persons had cancer – any type?
select COUNT(cpr) from diseases WHERE disease_name like "%cancer";

-- Who are or have been married to someone named ’Finn’?
select first_name from person where cpr IN (select female_cpr from marriage WHERE male_cpr IN (SELECT cpr FROM person WHERE first_name='Finn'));

-- Create 2 imaginary persons. Marry them to each other. Make them have a kid. Give the kid a broken nose. Insert all this info in the database.
INSERT INTO person VALUES ('040797-123', 'Christian','Jacobsen', 205, 80,'300363-123','140560-123');
INSERT INTO person VALUES ('250397-123', 'Anna','Bannana', 100, 50, '300362-123','140561-123');
INSERT INTO person VALUES ('120922-123', 'Ulrik','Bulrik', 205, 50, '120922-123','250397-123');
INSERT INTO marriage VALUES('040797-123','250397-123','11092022','12092022');
INSERT INTO disease VALUES('120922-123','Broken Nose','12092022');

-- Delete everyone with the last name ’Rapacki’. Make sure that database is consistent afterwards, like there is no marriages to non-existing persons or references to non-existing parents.
DELETE FROM person WHERE last_name='Rapacki';
UPDATE person SET father=NULL WHERE father NOT IN (SELECT cpr FROM person) and father <> '';
UPDATE person SET mother=NULL WHERE mother NOT IN (SELECT cpr FROM person) and mother <> '';
DELETE FROM marriage WHERE male_cpr NOT IN (SELECT cpr FROM person) or female_cpr NOT IN (SELECT cpr FROM person);
DELETE FROM diseases WHERE cpr NOT IN (SELECT cpr FROM person);

