"""PostgreSQL access layer — connection + CRUD for the `images` table.

No business logic here. Handlers call these functions, get plain dicts/ints back.
"""

import time
import logging
import psycopg2
import psycopg2.extras

from backend import config


# ── Connection ────────────────────────────────────────────────────────────────

def get_connection():
    """Open a psycopg2 connection. Retries up to 5 times with 2 s delay."""
    last_error = None
    for attempt in range(1, 6):
        try:
            return psycopg2.connect(**config.DB)
        except psycopg2.OperationalError as e:
            last_error = e
            logging.warning(f"DB connect attempt {attempt}/5 failed: {e}. Retrying in 2 s…")
            time.sleep(2)
    logging.error(f"DB connection failed after 5 attempts: {last_error}")
    raise last_error


def init_schema():
    """Execute db/init.sql — idempotent CREATE TABLE IF NOT EXISTS."""
    with open(config.SCHEMA_FILE, encoding="utf-8") as f:
        sql = f.read()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        logging.info("DB schema ready.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Schema init failed: {e}")
        raise
    finally:
        conn.close()


# ── Queries ───────────────────────────────────────────────────────────────────

def insert_image(filename: str, original_name: str, size: int, file_type: str) -> int:
    """INSERT a new row, return the generated id."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO images (filename, original_name, size, file_type)
                VALUES (%s, %s, %s, %s) RETURNING id
                """,
                (filename, original_name, size, file_type),
            )
            row_id = cur.fetchone()[0]
        conn.commit()
        return row_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_page(page: int) -> tuple[list[dict], int]:
    """Return (rows_for_page, total_count). Sorted by upload_time DESC."""
    offset = (page - 1) * config.PER_PAGE
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM images ORDER BY upload_time DESC LIMIT %s OFFSET %s",
                (config.PER_PAGE, offset),
            )
            rows = [dict(r) for r in cur.fetchall()]
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM images")
            total = cur.fetchone()[0]
        return rows, total
    finally:
        conn.close()


def fetch_by_id(image_id: int) -> dict | None:
    """Return the row dict or None if not found."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM images WHERE id = %s", (image_id,))
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def delete_by_id(image_id: int) -> bool:
    """DELETE the row. Return True if a row was actually removed."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM images WHERE id = %s", (image_id,))
            deleted = cur.rowcount > 0
        conn.commit()
        return deleted
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
