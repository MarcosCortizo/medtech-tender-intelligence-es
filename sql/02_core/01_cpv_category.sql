DROP TABLE IF EXISTS cpv_category;

CREATE TABLE cpv_category (
    cpv_code  CHAR(8)      NOT NULL PRIMARY KEY,
    cpv_label VARCHAR(100) NOT NULL,
    category  VARCHAR(30)  NOT NULL
);
