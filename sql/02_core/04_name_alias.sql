DROP TABLE IF EXISTS name_alias;

CREATE TABLE name_alias (
    entity       VARCHAR(10)   NOT NULL,
    variant_key  NVARCHAR(300) NOT NULL,
    official_key NVARCHAR(300) NOT NULL,
    reason       NVARCHAR(50)  NULL,
    CONSTRAINT pk_name_alias PRIMARY KEY (entity, variant_key)
);