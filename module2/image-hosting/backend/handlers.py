import json
from http.server import BaseHTTPRequestHandler

from utils.encoders import AppJSONEncoder
from config import settings


class BaseHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        
        self.wfile.write(json.dumps(data, cls=AppJSONEncoder).encode('utf-8'))
        
    def _send_error(self, status_code: int, message: str):
        self._send_json(status_code, {"error": message})
        
        
    def _path_parts(self) -> list | None:
        if not self.path.startswith(settings.api_prefix):
            return
        return [part for part in self.path.split("?")[0].split("/") if part not in ["", "api"]]
       
        
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        
    