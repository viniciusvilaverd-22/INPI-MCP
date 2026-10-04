\set ON_ERROR_STOP on

CREATE TABLE trademark_process (
    id VARCHAR(36) PRIMARY KEY,
    process_number VARCHAR(32) UNIQUE NOT NULL,
    mark_name TEXT
);

CREATE TABLE trademark_nice_class (
    id VARCHAR(36) PRIMARY KEY,
    trademark_id VARCHAR(36) NOT NULL REFERENCES trademark_process(id) ON DELETE CASCADE,
    nice_class INTEGER NOT NULL,
    edition VARCHAR(16),
    specification TEXT,
    CONSTRAINT uq_tm_class_spec UNIQUE (trademark_id, nice_class, specification)
);

INSERT INTO trademark_process (id, process_number, mark_name)
VALUES ('tm-1', '900000001', 'MIGRATION TEST');

INSERT INTO trademark_nice_class (id, trademark_id, nice_class, edition, specification)
VALUES
    ('nc-1', 'tm-1', 35, '13', 'Servicos de publicidade.'),
    ('nc-2', 'tm-1', 41, '13', NULL);
