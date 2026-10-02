-- Initial schema for Image Server 2.0.
-- Mounted into the postgres container's /docker-entrypoint-initdb.d/
-- so it runs automatically on first DB startup.

CREATE TABLE IF NOT EXISTS images (
    id            SERIAL PRIMARY KEY,
    filename      TEXT      NOT NULL,
    original_name TEXT      NOT NULL,
    size          INTEGER   NOT NULL,
    upload_time   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_type     TEXT      NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_images_upload_time ON images (upload_time DESC);
