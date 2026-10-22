DROP TABLE IF EXISTS dq_check_result;

CREATE TABLE dq_check_result (
    checked_at  DATETIME2    NOT NULL DEFAULT SYSUTCDATETIME(),
    check_name  VARCHAR(100) NOT NULL,
    bad_rows    INT          NOT NULL
);
