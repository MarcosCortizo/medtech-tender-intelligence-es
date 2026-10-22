DROP TABLE IF EXISTS supplier;

CREATE TABLE supplier (
    supplier_id   INT IDENTITY(1,1) PRIMARY KEY,
    supplier_key  NVARCHAR(300) NOT NULL,
    supplier_name NVARCHAR(300) NOT NULL,
    CONSTRAINT uq_supplier UNIQUE (supplier_key)
);