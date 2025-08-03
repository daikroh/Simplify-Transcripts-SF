-- Create database if it doesn't exist yet
SELECT 'CREATE DATABASE meetings' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'meetings')\gexec

-- Switch to meetings database
\c meetings;

CREATE TABLE IF NOT EXISTS records (
    record_id INTEGER PRIMARY KEY,
    view_id INTEGER,
    published_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agendas (
    agenda_id UUID PRIMARY KEY,
    record_id INTEGER,
    title VARCHAR(256),
    start_time INTEGER,
    end_time INTEGER,
    summary TEXT,
    transcript TEXT,
    CONSTRAINT fk_record_id
        FOREIGN KEY (record_id)
        REFERENCES records (record_id)
        ON DELETE CASCADE
);

-- List tables to check
\dt

-- Load data
\COPY transcripts_api_record FROM 'records.csv' WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');
\COPY transcripts_api_agendaitem(agenda_id, record_id, title, start_time, end_time, summary, transcript) FROM 'agendas.csv' WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',');