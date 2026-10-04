\set ON_ERROR_STOP on

DO $$
DECLARE
    state_table_count INTEGER;
    run_table_count INTEGER;
    singleton_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO state_table_count
    FROM pg_class
    WHERE relname = 'rpi_ingestion_state' AND relkind = 'r';

    SELECT COUNT(*) INTO run_table_count
    FROM pg_class
    WHERE relname = 'rpi_ingestion_run' AND relkind = 'r';

    SELECT COUNT(*) INTO singleton_count
    FROM rpi_ingestion_state
    WHERE id = 1;

    IF state_table_count <> 1 OR run_table_count <> 1 OR singleton_count <> 1 THEN
        RAISE EXCEPTION 'migration 003 tables/state singleton missing';
    END IF;
END $$;

UPDATE rpi_ingestion_state
SET last_ingested_rpi = 2908,
    last_checked_rpi = 2909,
    updated_at = now()
WHERE id = 1;

INSERT INTO rpi_ingestion_run (
    id,
    rpi_number,
    status,
    source_url,
    zip_sha256,
    xml_sha256,
    process_count,
    event_count,
    parser_version,
    finished_at
)
VALUES (
    'run-2908',
    2908,
    'completed',
    'https://revistas.inpi.gov.br/txt/RM2908.zip',
    repeat('a', 64),
    repeat('b', 64),
    39858,
    40201,
    'rpi-marcas-xml-0.2.1',
    now()
);

DO $$
DECLARE
    last_ingested INTEGER;
    last_checked INTEGER;
    completed_count INTEGER;
BEGIN
    SELECT last_ingested_rpi, last_checked_rpi
    INTO last_ingested, last_checked
    FROM rpi_ingestion_state
    WHERE id = 1;

    SELECT COUNT(*) INTO completed_count
    FROM rpi_ingestion_run
    WHERE rpi_number = 2908 AND status = 'completed';

    IF last_ingested <> 2908 OR last_checked <> 2909 OR completed_count <> 1 THEN
        RAISE EXCEPTION 'migration 003 state persistence validation failed';
    END IF;
END $$;
