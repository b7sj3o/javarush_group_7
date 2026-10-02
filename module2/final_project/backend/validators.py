"""Upload validation — extension, size, image integrity."""

import os
import uuid
from io import BytesIO

from PIL import Image

from backend import config


def extension_of(filename: str) -> str:
    """Lowercase extension without leading dot: 'Photo.JPG' → 'jpg'."""
    _, ext = os.path.splitext(filename)
    return ext.lower().lstrip(".")


def validate_extension(filename: str) -> str | None:
    """Return error message if extension not in ALLOWED_EXTENSIONS, else None."""
    ext = extension_of(filename)
    if ext not in config.ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(config.ALLOWED_EXTENSIONS))
        return f"File type '.{ext}' is not allowed. Accepted: {allowed}."
    return None


def validate_size(size: int) -> str | None:
    """Return error message if file exceeds MAX_FILE_SIZE, else None."""
    if size > config.MAX_FILE_SIZE:
        limit_mb = config.MAX_FILE_SIZE // (1024 * 1024)
        return f"File exceeds the {limit_mb} MB size limit."
    return None


def validate_image_bytes(data: bytes) -> str | None:
    """Confirm the bytes are a valid, decodable image via Pillow."""
    try:
        Image.open(BytesIO(data)).verify()
        return None
    except Exception as e:
        return f"File is not a valid image: {e}"


def generate_unique_name(original_name: str) -> str:
    """Return a UUID-based filename preserving the original extension."""
    ext = extension_of(original_name)
    return f"{uuid.uuid4().hex}.{ext}"
