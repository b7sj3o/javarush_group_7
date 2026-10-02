"""Entry point: logging, DB schema init, request router, HTTP server."""

import logging
import os
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

from backend import config, db, handlers, templates


# ── Logging ───────────────────────────────────────────────────────────────────

def setup_logging():
    os.makedirs(config.LOGS_DIR, exist_ok=True)
    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler(config.LOG_FILE)
    file_handler.setFormatter(fmt)

    stream_handler = logging.StreamHandler()   # also visible via `docker logs`
    stream_handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(file_handler)
    root.addHandler(stream_handler)


# ── Route table ───────────────────────────────────────────────────────────────
# Each entry: (HTTP-method, compiled-path-regex, handler-callable)

ROUTES = [
    ("GET",  re.compile(r"^/$"),             handlers.home),
    ("POST", re.compile(r"^/upload$"),       handlers.upload),
    ("GET",  re.compile(r"^/images-list$"),  handlers.images_list),
    ("POST", re.compile(r"^/delete/(\d+)$"), handlers.delete_image),
]


# ── Router ────────────────────────────────────────────────────────────────────

class Router(BaseHTTPRequestHandler):

    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")

    def _dispatch(self, method: str):
        path = self.path.split("?")[0]          # strip query string before matching
        for route_method, pattern, handler in ROUTES:
            if route_method != method:
                continue
            m = pattern.match(path)
            if m:
                # convert digit captures to int (e.g. image_id in /delete/<id>)
                args = [int(g) if g.isdigit() else g for g in m.groups()]
                handler(self, *args)
                return
        self.send_html(404, templates.error_page("Page not found.", 404))

    # ── Response helpers used by handlers ─────────────────────────────────────

    def send_html(self, status: int, body: str):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def send_redirect(self, location: str):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def log_message(self, *_):
        return   # silence default stderr access log; we use our own logger


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    setup_logging()
    db.init_schema()
    server = HTTPServer((config.HOST, config.PORT), Router)
    logging.info(f"Server listening on {config.HOST}:{config.PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
