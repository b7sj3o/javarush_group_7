"""HTML rendering layer.

Loads files from frontend/templates/ and fills {placeholders} with values.
Uses simple str.replace (not str.format) so that already-rendered HTML injected
as a context value cannot accidentally trigger further substitutions.
User-provided strings are always html.escape()'d before injection.
"""

import html as _html
import os

from backend import config


def render(template_name: str, **context) -> str:
    """Load a template file and replace every {key} with its value (one pass)."""
    path = os.path.join(config.TEMPLATES_DIR, template_name)
    with open(path, encoding="utf-8") as f:
        tmpl = f.read()
    for key, value in context.items():
        tmpl = tmpl.replace("{" + key + "}", str(value))
    return tmpl


def _wrap(title: str, content: str) -> str:
    return render("base.html", title=title, content=content)


# ── Page renderers ────────────────────────────────────────────────────────────

def home() -> str:
    return _wrap("Image Server", render("home.html"))


def upload_success(filename: str, original_name: str) -> str:
    inner = render(
        "success.html",
        filename=filename,
        original_name=_html.escape(original_name),
    )
    return _wrap("Upload successful", inner)


def images_list(rows: list[dict], page: int, has_prev: bool, has_next: bool) -> str:
    row_html = (
        "\n".join(_build_row(r) for r in rows)
        if rows
        else '<tr><td colspan="6" class="empty">No images uploaded yet.</td></tr>'
    )
    prev_link = (
        f'<a href="/images-list?page={page - 1}" class="btn">&#8592; Prev</a>'
        if has_prev
        else '<span class="btn btn-disabled">&#8592; Prev</span>'
    )
    next_link = (
        f'<a href="/images-list?page={page + 1}" class="btn">Next &#8594;</a>'
        if has_next
        else '<span class="btn btn-disabled">Next &#8594;</span>'
    )
    inner = render(
        "list.html",
        rows=row_html,
        page=str(page),
        prev_link=prev_link,
        next_link=next_link,
    )
    return _wrap(f"Images — page {page}", inner)


def error_page(message: str, status: int) -> str:
    inner = render("error.html", status=str(status), message=_html.escape(message))
    return _wrap(f"Error {status}", inner)


# ── Private helpers ───────────────────────────────────────────────────────────

def _build_row(r: dict) -> str:
    name    = _html.escape(r["filename"])
    orig    = _html.escape(r["original_name"])
    size_kb = max(1, r["size"] // 1024)
    ts      = r["upload_time"].strftime("%Y-%m-%d %H:%M")
    ftype   = _html.escape(r["file_type"])
    row_id  = r["id"]
    return (
        f"<tr>"
        f'<td><a href="/images/{name}">{name}</a></td>'
        f"<td>{orig}</td>"
        f"<td>{size_kb} KB</td>"
        f"<td>{ts}</td>"
        f"<td>{ftype}</td>"
        f"<td>"
        f'<form method="post" action="/delete/{row_id}" style="margin:0">'
        f'<button class="btn btn-danger" type="submit">Delete</button>'
        f"</form>"
        f"</td>"
        f"</tr>"
    )
