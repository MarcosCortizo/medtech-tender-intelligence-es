DROP TABLE IF EXISTS notice_category;

CREATE TABLE notice_category (
    publication_number VARCHAR(20) NOT NULL REFERENCES notice (publication_number),
    category           VARCHAR(30) NOT NULL,
    PRIMARY KEY (publication_number, category)
);