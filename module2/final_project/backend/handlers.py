"""Per-route handlers — HTTP plumbing only.

Each function receives the Router request object and writes a response.
Validation → validators, SQL → db, HTML → templates.
"""

import cgi
import logging
import os

from backend import config, db, templates, validators


def home(request):
    """GET /"""
    request.send_html(200, templates.home())


def upload(request):
    """POST /upload — validate, save file, insert DB row, show success page."""
    # cgi.FieldStorage is deprecated in Python 3.11+ but still present in 3.12
    form = cgi.FieldStorage(
        fp=request.rfile,
        headers=request.headers,
        environ={
            "REQUEST_METHOD": "POST",
            "CONTENT_TYPE": request.headers.get("Content-Type", ""),
            "CONTENT_LENGTH": request.headers.get("Content-Length", "0"),
        },
    )

    if "file" not in form:
        request.send_html(400, templates.error_page("No file provided.", 400))
        return

    file_item     = form["file"]
    original_name = file_item.filename or "upload"
    data          = file_item.file.read()
    size          = len(data)

    # run all validations; return on the first failure
    for error in (
        validators.validate_extension(original_name),
        validators.validate_size(size),
        validators.validate_image_bytes(data),
    ):
        if error:
            logging.warning(f"Upload rejected '{original_name}': {error}")
            request.send_html(400, templates.error_page(error, 400))
            return

    unique_name = validators.generate_unique_name(original_name)
    file_path   = os.path.join(config.IMAGES_DIR, unique_name)
    ext         = validators.extension_of(original_name)

    # write file to disk
    try:
        with open(file_path, "wb") as f:
            f.write(data)
    except OSError as e:
        logging.error(f"Failed to write '{unique_name}': {e}")
        request.send_html(500, templates.error_page("Could not save the file.", 500))
        return

    # persist metadata; roll back the file on DB failure
    try:
        db.insert_image(unique_name, original_name, size, ext)
    except Exception as e:
        logging.error(f"DB insert failed for '{unique_name}': {e}")
        os.remove(file_path)
        request.send_html(500, templates.error_page("Database error.", 500))
        return

    logging.info(f"Uploaded: '{original_name}' → '{unique_name}' ({size} bytes)")
    request.send_html(200, templates.upload_success(unique_name, original_name))


def images_list(request):
    """GET /images-list?page=N"""
    page         = _parse_page(request.path)
    rows, total  = db.fetch_page(page)
    has_prev     = page > 1
    has_next     = (page * config.PER_PAGE) < total
    request.send_html(200, templates.images_list(rows, page, has_prev, has_next))


def delete_image(request, image_id: int):
    """POST /delete/<id> — remove file from disk and DB, redirect to list."""
    record = db.fetch_by_id(image_id)
    if not record:
        request.send_html(404, templates.error_page(f"Image #{image_id} not found.", 404))
        return

    file_path = os.path.join(config.IMAGES_DIR, record["filename"])
    try:
        os.remove(file_path)
    except FileNotFoundError:
        logging.warning(f"File missing on disk during delete: {record['filename']}")
    except OSError as e:
        logging.error(f"Could not delete file '{record['filename']}': {e}")

    db.delete_by_id(image_id)
    logging.info(f"Deleted image #{image_id}: {record['filename']}")
    request.send_redirect("/images-list")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_page(raw_path: str) -> int:
    """Extract ?page=N from the request path. Returns 1 on missing/invalid."""
    if "?" not in raw_path:
        return 1
    query = raw_path.split("?", 1)[1]
    for part in query.split("&"):
        if part.startswith("page="):
            try:
                return max(1, int(part[5:]))
            except ValueError:
                return 1
    return 1
