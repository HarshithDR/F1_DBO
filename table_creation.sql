--------------------------------------------
-- CREATE DATABASE --
--------------------------------------------
CREATE DATABASE f1racing;
USE f1racing;
SELECT DATABASE();

--------------------------------------------
-- CREATE RELATED TABLES --
--------------------------------------------
CREATE TABLE Team(
	TeamName varchar(40) not null,
    Base varchar(50),
    TeamChief varchar(40) not null,
    TechnicalChief varchar(40) not null,
    Chassis varchar(25),
    PowerUnit varchar(25),
    FirstTeamEntry int,
    WorldChampionships int,
    HighestRaceFinish int,
    PolePosition int,
	FastestLaps int,
	PRIMARY KEY(TeamName)
);

CREATE TABLE Driver(
	DriverID int,
    Name varchar(40) not null,
    TeamName varchar(40),
    Country varchar(30),
    Podiums int,
    Points int,
    GrandPrixEntered int,
    WorldChampionships int,
    HighestRaceFinish int,
    DateOfBirth date,
	GlobalRank int,
	PRIMARY KEY(DriverID),
    FOREIGN KEY(TeamName) REFERENCES Team(TeamName)
);

CREATE TABLE F1Awards(
	AwardID int,
    DriverID int,
    AwardName varchar(50) not null,
    AwardDescription varchar(100) not null,
    AwardImage varchar(255),
    Date date,
	PRIMARY KEY(AwardID),
    FOREIGN KEY(DriverID) REFERENCES Driver(DriverID)
);

CREATE TABLE RaceTrack(
	TrackName varchar(100) not null,
    FirstGrandPrix int,
    NumberOfLaps int,
    LapRecord decimal(6,3),
    RaceDistance decimal(5,2),
    CircuitLength decimal(4,3),
	PRIMARY KEY(TrackName)
);

CREATE TABLE Race(
	RaceID int,
    Laps int,
	Location varchar(50),
    TrackName varchar(100) not null,
	PRIMARY KEY(RaceID),
    FOREIGN KEY(TrackName) REFERENCES RaceTrack(TrackName)
);

CREATE TABLE RaceSchedule(
	ScheduleID int,
	RaceID int,
    TrackName varchar(100),
    StartTime time,
    EndTime time,
	Date date,
    Broadcaster varchar(40),
	PRIMARY KEY(ScheduleID),
    FOREIGN KEY(RaceID) REFERENCES Race(RaceID)
);

CREATE TABLE RaceDriverDetails(
	RaceID int,
    DriverID int,
	Car varchar(50),
    RacePoints int,f1awards
    TimeRetired time,
    Position int,
	PRIMARY KEY(RaceID, DriverID),
    FOREIGN KEY(RaceID) REFERENCES Race(RaceID),
	FOREIGN KEY(DriverID) REFERENCES Driver(DriverID)
);

SHOW TABLES;

----------------------------------------------------------
-- Check table content after loading the data
-----------------------------------------------------------
SELECT * FROM Team;
SELECT * FROM Driver;
SELECT * FROM F1Awards;
SELECT * FROM RaceTrack;
SELECT * FROM Race;
SELECT * FROM RaceSchedule;
SELECT * FROM RaceDriverDetails;

--------------------------------------------------------------
-- Insert data into any table (E.g., F1Awards)
--------------------------------------------------------------
INSERT INTO F1Awards (AwardID, DriverID, AwardName, AwardDescription, AwardImage, Date)
VALUES (16, 8, 'lnunc vestibulum', 'kanskh kjsdhfhe jhuwbjfi', '/path/to/file1.jpg', '2023-06-08');

SELECT * FROM F1Awards WHERE AwardID = 16;

--------------------------------------------------------------
-- Update data in table (E.g., F1Awards)
--------------------------------------------------------------
SELECT * FROM F1Awards WHERE AwardID = 16;

UPDATE F1Awards
SET 
    DriverID = 1, 
    AwardName = 'updated award name', 
    AwardDescription = 'updated description',
    AwardImage = '/new/path/to/file2.jpg', 
    Date = '2023-11-21'
WHERE 
    AwardID = 16;
 
 SELECT * FROM F1Awards WHERE AwardID = 16;
 
--------------------------------------------------------------
-- Delete data from table (E.g., F1Awards)
--------------------------------------------------------------
SELECT * FROM F1Awards WHERE AwardID = 16;

DELETE FROM F1Awards
WHERE 
    AwardID = 16;

SELECT * FROM F1Awards WHERE AwardID = 16;

--------------------------------------------------------------
-- INDEXES - Creating a new index (E.g., RaceSchedule)
--------------------------------------------------------------

-- 1. Creating a new index on TrackName attribute from RaceSchedule table
SHOW INDEX FROM RaceSchedule;

CREATE INDEX Track_index ON RaceSchedule(TrackName);

SHOW INDEX FROM RaceSchedule;

-----------------------------------------------------------------

-- 2. Creating a new index on Location attribute from Race table
SHOW INDEX FROM Race;

CREATE INDEX Location_index ON Race(Location);

SHOW INDEX FROM Race;

--------------------------------------------------------------
-- VIEWS - Creating new views
--------------------------------------------------------------

-- Creating a view which will have drivers from china who met certain conditions given below
CREATE VIEW drivers_from_china AS
	SELECT d.Name, t.TeamName, rd.Car
    FROM Driver d, Team t, RaceDriverDetails rd
    WHERE d.TeamName = t.TeamName AND d.DriverID = rd.DriverID AND d.Country = 'China';
    
SELECT * FROM drivers_from_china;

DROP VIEW drivers_from_china;

--------------------------------------------------------------
-- TEMPORARY TABLES --
--------------------------------------------------------------

-- 1. Create a temporary table that includes drivers who have won more than one F1 award.

CREATE TEMPORARY TABLE MultipleF1AwardsWinners AS
SELECT DriverID, COUNT(AwardID) as NumberOfAwards
FROM F1Awards 
GROUP BY DriverID
HAVING COUNT(AwardID) > 1;

SELECT * FROM MultipleF1AwardsWinners;

DROP VIEW MultipleF1AwardsWinners; 


--------------------------------------------------------------
-- TRIGGERS --
--------------------------------------------------------------

-- Trigger to check each award in the F1Awards table can only be associated with one driver.

DELIMITER //
CREATE TRIGGER check_single_driver_per_award
BEFORE INSERT ON F1Awards
FOR EACH ROW
BEGIN
    DECLARE existing_driver_id INT;
    
    -- Check if there is already an entry for the AwardID.
    SELECT DriverID INTO existing_driver_id
    FROM F1Awards
    WHERE AwardID = NEW.AwardID
    LIMIT 1;
    
    -- If there is an existing driver for the award and it's different from the new one, throw an error.
    IF existing_driver_id IS NOT NULL AND existing_driver_id != NEW.DriverID THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Each F1Award should only be associated with one driver.';
    END IF;
END;

// DELIMITER ;

Select * from F1Awards;

-- Insert initial test data
INSERT INTO F1Awards (AwardID, DriverID, AwardName, AwardDescription, AwardImage, Date)
VALUES (16, 2, 'lnunc vestibulum', 'kanskh kjsdhfhe jhuwbjfi', '/path/to/file1.jpg', '2023-06-08');

-- Test Case 1: This should succeed
INSERT INTO F1Awards (AwardID, DriverID, AwardName, AwardDescription, AwardImage, Date)
VALUES (17, 3, 'asdkjabsdk adskahsdk', 'akjsdhak', '/path/to/file2.jpg', '2023-09-05');

-- Test Case 2: This should fail
INSERT INTO F1Awards (AwardID, DriverID, AwardName, AwardDescription, AwardImage, Date)
VALUES (16, 3, 'lnunc vestibulum', 'kanskh kjsdhfhe jhuwbjfi', '/path/to/file1.jpg', '2023-06-08');


--------------------------------------------------------------
-- STORED PROCEDURES --
--------------------------------------------------------------
-- Stored Procedure to insert both Race and RaceSchedule, so that a Race must have a single RaceSchedule

DELIMITER //
CREATE PROCEDURE insert_race_with_schedule(
    IN race_id INT,
    IN schedule_id INT,
    IN laps INT,
    IN location varchar(50),
    IN trackName varchar(100),
    IN broadcaster VARCHAR(40),
    IN start_time TIME,
    IN end_time TIME,
    IN date DATE
)
BEGIN
    INSERT INTO Race (RaceID, Laps, Location, TrackName)
    VALUES (race_id, laps, location, trackName);

    INSERT INTO RaceSchedule (ScheduleID, RaceID, TrackName, StartTime, EndTime, Date, Broadcaster)
    VALUES (schedule_id, raceID, trackName, start_time, end_time, date, broadcaster);
END;
//
DELIMITER ;

CALL insert_race_with_schedule(31, 16, 100, 'erat curabitur', 'Yas Marina Circuit ','Sports Network', '13:00', '15:00', '2023-07-20');

SELECT * FROM Race WHERE RaceID = 31;
SELECT * FROM RaceSchedule WHERE ScheduleID = 16;

DROP PROCEDURE insert_race_with_schedule;


--------------------------------------------------------------
-- FUNCTIONS --
--------------------------------------------------------------
-- A function to check if each RaceDriverDetails belongs to exactly one Race.
 
 DELIMITER //
 CREATE FUNCTION check_race_driver_details_belongs_to_race(
    race_id INT,
    driver_id INT
)
RETURNS INTEGER
DETERMINISTIC

BEGIN
    DECLARE race_count INT;
    SELECT COUNT(*) INTO race_count FROM RaceDriverDetails WHERE RaceID = race_id AND DriverID = driver_id;
    IF race_count = 1 THEN
        RETURN 1;
    ELSE
        RETURN 0;
    END IF;
END;
//
DELIMITER ;

SELECT check_race_driver_details_belongs_to_race(9, 14) AS result;

DROP FUNCTION check_race_driver_details_belongs_to_race;
