BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
    IF to_regclass('public.trademark_nice_class') IS NULL THEN
        RAISE EXCEPTION 'trademark_nice_class table does not exist; migration 002 requires an existing schema';
    END IF;
END $$;

ALTER TABLE trademark_nice_class
    ADD COLUMN IF NOT EXISTS specification_hash VARCHAR(64);

UPDATE trademark_nice_class
SET specification_hash = encode(
    digest(convert_to(COALESCE(specification, ''), 'UTF8'), 'sha256'),
    'hex'
)
WHERE specification_hash IS NULL
   OR specification_hash !~ '^[0-9a-f]{64}$';

DO $$
DECLARE
    duplicate_groups BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO duplicate_groups
    FROM (
        SELECT trademark_id, nice_class, specification_hash
        FROM trademark_nice_class
        GROUP BY trademark_id, nice_class, specification_hash
        HAVING COUNT(*) > 1
    ) AS duplicates;

    IF duplicate_groups > 0 THEN
        RAISE EXCEPTION
            'migration 002 aborted: % duplicate trademark/class/specification hash groups require manual review',
            duplicate_groups;
    END IF;
END $$;

ALTER TABLE trademark_nice_class
    ALTER COLUMN specification_hash SET NOT NULL;

ALTER TABLE trademark_nice_class
    DROP CONSTRAINT IF EXISTS uq_tm_class_spec;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'trademark_nice_class'::regclass
          AND conname = 'uq_tm_class_spec_hash'
    ) THEN
        ALTER TABLE trademark_nice_class
            ADD CONSTRAINT uq_tm_class_spec_hash
            UNIQUE (trademark_id, nice_class, specification_hash);
    END IF;
END $$;

COMMIT;
