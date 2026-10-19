DROP TABLE IF EXISTS stop_events CASCADE;
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS line_stops CASCADE;
DROP TABLE IF EXISTS stops CASCADE;
DROP TABLE IF EXISTS lines CASCADE;

DROP TABLE IF EXISTS stop_lines CASCADE;

CREATE TABLE lines (
    line_name VARCHAR(50) PRIMARY KEY,
    vehicle_type VARCHAR(10) NOT NULL CHECK (vehicle_type IN ('rail', 'bus'))
);

CREATE TABLE stops (
    stop_name VARCHAR(100) PRIMARY KEY,
    latitude NUMERIC(9,6) NOT NULL,
    longitude NUMERIC(9,6) NOT NULL
);

CREATE TABLE line_stops (
    line_name VARCHAR(50) REFERENCES lines(line_name),
    stop_name VARCHAR(100) REFERENCES stops(stop_name),
    sequence INTEGER NOT NULL CHECK (sequence > 0),
    time_offset INTEGER NOT NULL CHECK (time_offset >= 0),
    PRIMARY KEY (line_name, sequence)
);

CREATE TABLE trips (
    trip_id VARCHAR(20) PRIMARY KEY,
    line_name VARCHAR(50) NOT NULL REFERENCES lines(line_name),
    scheduled_departure TIMESTAMP NOT NULL,
    vehicle_id VARCHAR(20) NOT NULL
);

CREATE TABLE stop_events (
    trip_id VARCHAR(20) REFERENCES trips(trip_id),
    stop_name VARCHAR(100) REFERENCES stops(stop_name),
    scheduled TIMESTAMP NOT NULL,
    actual TIMESTAMP NOT NULL,
    passengers_on INTEGER NOT NULL CHECK (passengers_on >= 0),
    passengers_off INTEGER NOT NULL CHECK (passengers_off >= 0),
    PRIMARY KEY (trip_id, stop_name)
);
