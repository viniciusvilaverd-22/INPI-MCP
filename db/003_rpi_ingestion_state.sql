BEGIN;

CREATE TABLE IF NOT EXISTS rpi_ingestion_state (
    id INTEGER PRIMARY KEY,
    last_ingested_rpi INTEGER,
    last_checked_rpi INTEGER,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO rpi_ingestion_state (id, last_ingested_rpi, last_checked_rpi)
VALUES (1, NULL, NULL)
ON CONFLICT (id) DO NOTHING;

CREATE TABLE IF NOT EXISTS rpi_ingestion_run (
    id VARCHAR(36) PRIMARY KEY,
    rpi_number INTEGER NOT NULL UNIQUE,
    status VARCHAR(16) NOT NULL,
    source_url TEXT,
    zip_sha256 VARCHAR(64),
    xml_sha256 VARCHAR(64),
    process_count INTEGER,
    event_count INTEGER,
    parser_version VARCHAR(64),
    error TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_rpi_ingestion_run_rpi_number
    ON rpi_ingestion_run (rpi_number);

CREATE INDEX IF NOT EXISTS ix_rpi_ingestion_run_status
    ON rpi_ingestion_run (status);

COMMIT;
