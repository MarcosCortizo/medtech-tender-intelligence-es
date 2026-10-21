DROP TABLE IF EXISTS buyer;

CREATE TABLE buyer (
    buyer_id   INT IDENTITY(1,1) PRIMARY KEY,
    buyer_name NVARCHAR(300) NOT NULL,
    buyer_city NVARCHAR(100),
    CONSTRAINT uq_buyer UNIQUE (buyer_name)
);
