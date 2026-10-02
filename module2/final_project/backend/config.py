"""Centralised configuration: env vars, paths, limits."""

import os


# ── Paths (inside container) ──────────────────────────────────────────────────

IMAGES_DIR    = "/images"
LOGS_DIR      = "/logs"
TEMPLATES_DIR = "/app/frontend/templates"
STATIC_DIR    = "/app/frontend/static"
LOG_FILE      = f"{LOGS_DIR}/app.log"


# ── Upload constraints ────────────────────────────────────────────────────────

MAX_FILE_SIZE      = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}


# ── Pagination ────────────────────────────────────────────────────────────────

PER_PAGE = 10


# ── Database ──────────────────────────────────────────────────────────────────

DB = {
    "dbname":   os.getenv("DB_NAME",     "images_db"),
    "user":     os.getenv("DB_USER",     "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "host":     os.getenv("DB_HOST",     "db"),
    "port":     os.getenv("DB_PORT",     "5432"),
}


# ── Database schema file (inside container) ──────────────────────────────────

SCHEMA_FILE = "/app/db/init.sql"


# ── Server ────────────────────────────────────────────────────────────────────

HOST = "0.0.0.0"
PORT = 8000
