DROP TABLE IF EXISTS lot;

CREATE TABLE lot (
    publication_number VARCHAR(20)   NOT NULL REFERENCES notice (publication_number),
    lot_id             VARCHAR(20)   NOT NULL,
    supplier_id        INT           NULL REFERENCES supplier (supplier_id),
    estimated_value    DECIMAL(18,2),
    tender_value       DECIMAL(18,2),
    currency           CHAR(3),
    tenders_received   INT,
    deadline_date      DATE,
    duration_value     INT,
    duration_unit      VARCHAR(10),
    contract_date      DATE,
    PRIMARY KEY (publication_number, lot_id)
);