CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE OR REPLACE PROCEDURE ecommerce.anonymize_user(target_user_id uuid, hashed_value varchar)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 1. Scrub PII from the profile table
    UPDATE
        ecommerce.users
    SET
        first_name = encode(digest(first_name || hashed_value, 'sha256'), 'hex'),
        last_name = encode(digest(last_name || hashed_value, 'sha256'), 'hex'),
        phone = encode(digest(phone || hashed_value, 'sha256'), 'hex'),
        email = encode(digest(email || hashed_value, 'sha256'), 'hex') || '@deleted.com',
        address_line1 = encode(digest(address_line1 || hashed_value, 'sha256'), 'hex'),
        is_deleted = TRUE,
        deleted_at = NOW()
    WHERE
        user_id = target_user_id;
    -- 2. Break the link to analytics by dropping the mapping row
    DELETE FROM ecommerce.user_id_map
    WHERE user_id = target_user_id;
    COMMIT;
END;
$$;

