DROP TABLE IF EXISTS stg_lot;
DROP TABLE IF EXISTS stg_notice;

CREATE TABLE stg_notice (
    publication_number   VARCHAR(20)    NOT NULL PRIMARY KEY,
    notice_id            VARCHAR(50),
    procedure_id         VARCHAR(50),
    notice_type          VARCHAR(20),
    form_type            VARCHAR(20),
    publication_date     DATE,
    dispatch_date        DATE,
    buyer_name           NVARCHAR(300),
    buyer_city           NVARCHAR(100),
    title                NVARCHAR(2000),
    cpv_codes            VARCHAR(500),
    estimated_value_proc DECIMAL(18,2),
    notice_url           VARCHAR(200),
    loaded_at            DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE stg_lot (
    publication_number VARCHAR(20)   NOT NULL,
    lot_id             VARCHAR(20)   NOT NULL,
    estimated_value    DECIMAL(18,2),
    tender_value       DECIMAL(18,2),
    currency           CHAR(3),
    winner_name        NVARCHAR(300),
    tenders_received   INT,
    deadline_date      DATE,
    duration_value     INT,
    duration_unit      VARCHAR(10),
    contract_date      DATE,
    loaded_at          DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    PRIMARY KEY (publication_number, lot_id)
);
