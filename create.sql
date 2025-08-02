-- Create database if it doesn't exist yet
SELECT 'CREATE DATABASE meetings' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'meetings')\gexec

-- Switch to meetings database
\c meetings;

CREATE TABLE IF NOT EXISTS records (
    record_id INTEGER PRIMARY KEY,
    category VARCHAR(128),
    video_src VARCHAR(128),
    agenda_src VARCHAR(128),
    published_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agendas (
    agenda_id UUID PRIMARY KEY,
    record_id INTEGER,
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