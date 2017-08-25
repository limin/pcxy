-- Run sql with command: sqlite3 file.db < file.sql 

-- DROP TABLE domains;
CREATE TABLE IF NOT EXISTS domains(name text, tags text);
CREATE INDEX index_domain_name ON domains (name);
