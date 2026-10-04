\set ON_ERROR_STOP on

DO $$
DECLARE
    bad_hashes BIGINT;
    old_constraint BIGINT;
    new_constraint BIGINT;
BEGIN
    SELECT COUNT(*) INTO bad_hashes
    FROM trademark_nice_class
    WHERE specification_hash IS NULL
       OR specification_hash !~ '^[0-9a-f]{64}$';

    IF bad_hashes <> 0 THEN
        RAISE EXCEPTION 'invalid specification hashes after migration';
    END IF;

    SELECT COUNT(*) INTO old_constraint
    FROM pg_constraint
    WHERE conrelid='trademark_nice_class'::regclass
      AND conname='uq_tm_class_spec';

    SELECT COUNT(*) INTO new_constraint
    FROM pg_constraint
    WHERE conrelid='trademark_nice_class'::regclass
      AND conname='uq_tm_class_spec_hash';

    IF old_constraint <> 0 OR new_constraint <> 1 THEN
        RAISE EXCEPTION 'unexpected migration constraints';
    END IF;
END $$;

INSERT INTO trademark_nice_class (
    id, trademark_id, nice_class, edition, specification, specification_hash
)
VALUES (
    'nc-long',
    'tm-1',
    28,
    '13',
    repeat('Item de classe; ', 700),
    encode(digest(convert_to(repeat('Item de classe; ', 700), 'UTF8'), 'sha256'), 'hex')
);

DO $$
DECLARE
    long_len INTEGER;
BEGIN
    SELECT length(specification)
    INTO long_len
    FROM trademark_nice_class
    WHERE id='nc-long';

    IF long_len < 8000 THEN
        RAISE EXCEPTION 'long specification was not preserved';
    END IF;
END $$;

SELECT
    COUNT(*) AS rows_after_migration,
    COUNT(*) FILTER (WHERE specification_hash ~ '^[0-9a-f]{64}$') AS valid_hashes,
    MAX(length(specification)) AS max_specification_length
FROM trademark_nice_class;
