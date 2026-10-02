# ── Stage 1: install dependencies ────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /install
COPY requirements.txt .
RUN pip install --prefix=/install/packages --no-cache-dir -r requirements.txt


# ── Stage 2: runtime image ───────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# packages from builder
COPY --from=builder /install/packages /usr/local

# application source
COPY backend  ./backend
COPY frontend ./frontend
COPY db       ./db

# volume mount points
RUN mkdir -p /images /logs

EXPOSE 8000

RUN useradd -m appuser && chown -R appuser /app /images /logs
USER appuser

CMD ["python", "-m", "backend.main"]
