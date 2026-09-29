-- ================================================================
-- Fitbit Fitness Tracker - schema
-- Source: Fitabase export, 33 users, 4/12/2016 - 5/12/2016
-- ================================================================

CREATE DATABASE IF NOT EXISTS fitbit_analysis;
USE fitbit_analysis;

-- --------------------------------------------------------------
-- users: just the distinct device IDs. The raw data has no name,
-- age or demographic fields, so this table only exists to give the
-- fact tables something to reference with a foreign key.
-- --------------------------------------------------------------
CREATE TABLE users (
    Id BIGINT PRIMARY KEY
);

-- --------------------------------------------------------------
-- daily_activity: one row per user per day (from daily_activity_clean.csv)
-- --------------------------------------------------------------
CREATE TABLE daily_activity (
    Id                          BIGINT NOT NULL,
    Date                        DATE NOT NULL,
    TotalSteps                  INT,
    TotalDistance                DECIMAL(6,2),
    LoggedActivitiesDistance     DECIMAL(6,2),
    VeryActiveDistance           DECIMAL(6,2),
    ModeratelyActiveDistance     DECIMAL(6,2),
    LightActiveDistance          DECIMAL(6,2),
    SedentaryActiveDistance      DECIMAL(6,2),
    VeryActiveMinutes           INT,
    FairlyActiveMinutes         INT,
    LightlyActiveMinutes        INT,
    SedentaryMinutes            INT,
    Calories                    INT,
    DeviceWorn                  BOOLEAN,
    DayOfWeek                   VARCHAR(10),
    IsWeekend                   BOOLEAN,
    TotalActiveMinutes          INT,
    PRIMARY KEY (Id, Date),
    FOREIGN KEY (Id) REFERENCES users(Id)
);

-- --------------------------------------------------------------
-- hourly_activity: one row per user per hour (merged from the three
-- hourly Fitabase files: calories, intensities, steps)
-- --------------------------------------------------------------
CREATE TABLE hourly_activity (
    Id               BIGINT NOT NULL,
    DateTime         DATETIME NOT NULL,
    Calories         INT,
    TotalIntensity   INT,
    AverageIntensity DECIMAL(5,2),
    StepTotal        INT,
    Hour             TINYINT,
    PRIMARY KEY (Id, DateTime),
    FOREIGN KEY (Id) REFERENCES users(Id)
);

-- --------------------------------------------------------------
-- sleep_log: one row per user per night they logged sleep
-- (only 24 of the 33 users ever appear here)
-- --------------------------------------------------------------
CREATE TABLE sleep_log (
    Id                    BIGINT NOT NULL,
    Date                  DATE NOT NULL,
    TotalSleepRecords     INT,
    TotalMinutesAsleep    INT,
    TotalTimeInBed        INT,
    MinutesInBedNotAsleep INT,
    PRIMARY KEY (Id, Date),
    FOREIGN KEY (Id) REFERENCES users(Id)
);

-- --------------------------------------------------------------
-- weight_log: one row per weigh-in (only 8 of the 33 users
-- ever logged their weight)
-- --------------------------------------------------------------
CREATE TABLE weight_log (
    LogId          BIGINT PRIMARY KEY,
    Id             BIGINT NOT NULL,
    Date           DATETIME NOT NULL,
    WeightKg       DECIMAL(5,2),
    WeightPounds   DECIMAL(6,2),
    BMI            DECIMAL(5,2),
    IsManualReport BOOLEAN,
    FOREIGN KEY (Id) REFERENCES users(Id)
);

-- --------------------------------------------------------------
-- Indexes: Id is already covered as the first column of every
-- composite primary key above, so lookups by user are fast without
-- extra indexes. The one useful addition is a Date index for the
-- range-based queries (weekly/date-range filters) used in the app.
-- --------------------------------------------------------------
CREATE INDEX idx_daily_date ON daily_activity(Date);
CREATE INDEX idx_sleep_date ON sleep_log(Date);
