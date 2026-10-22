DROP TABLE IF EXISTS notice;

CREATE TABLE notice (
    publication_number   VARCHAR(20)    NOT NULL PRIMARY KEY,
    procedure_id         VARCHAR(50),
    notice_type          VARCHAR(20),
    form_type            VARCHAR(20),
    publication_date     DATE,
    buyer_id             INT            NOT NULL REFERENCES buyer (buyer_id),
    buyer_city           NVARCHAR(100),
    title                NVARCHAR(2000),
    estimated_value_proc DECIMAL(18,2),
    notice_url           VARCHAR(200)
);