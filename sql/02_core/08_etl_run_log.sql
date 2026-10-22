DROP TABLE IF EXISTS etl_run_log;

CREATE TABLE etl_run_log (
    run_id        INT IDENTITY(1,1) PRIMARY KEY,
    started_at    DATETIME2      NOT NULL,
    finished_at   DATETIME2      NOT NULL,
    status        VARCHAR(10)    NOT NULL,
    new_notices   INT,
    new_lots      INT,
    error_message NVARCHAR(1000)
);