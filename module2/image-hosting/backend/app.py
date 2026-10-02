import os
import cgi
import math
import uuid
from http.server import HTTPServer

from logger import logger
from database import ImageRepository
from config import settings
from handlers import BaseHandler
from utils import (
    get_query_params, 
    validate_size, 
    validate_extension, 
    save_image,
    image_exists,
    delete_image
)


class ImageAPIServer(BaseHandler):
    def __init__(self, *args, **kwargs):
        self.repo = ImageRepository()
        super().__init__(*args, **kwargs)

        
    def get_images(self):
        params = get_query_params(self.path)

        page = int(params['page']) if params.get('page', '').isdigit() else 1
        limit = int(params['limit']) if params.get('limit', '').isdigit() else 10
        order = params.get('order', "desc")

        items = self.repo.list(page=page, limit=limit, direction=order)
        total = self.repo.count()
        pages = max(1, math.ceil(total / limit))

        self._send_json(200, {
            "items": items,
            "pagination": {
                "total": total,
                "pages": pages,
                "page": page,
                "limit": limit,
            },
        })


    def get_image(self):
        filename = self.path.split("?")[0].split("/")[-1]
        
        image = self.repo.get_by_filename(filename)
        
        if image is None:
            logger.error(f"Image '{filename}' not found")
            self._send_error(404, "Not Found")
            return
            
        
        self._send_json(200, image)


    def create_image(self):
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self._send_error(400, "Expected multipart/form-data")
            return
        
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={"REQUEST_METHOD": "POST"},
        )
        
        if "file" not in form:
            self._send_error(400, "No file provided")
            return
        
        file_item = form["file"]
        if not file_item.filename:
            self._send_error(400, "No file provided")
            return
        
        original_name: str = file_item.filename
        data: bytes = file_item.file.read()
        
        if not validate_extension(original_name):
            self._send_error(400, f"Invalid file type. Allowed: {settings.allowed_file_types}")
            return
            
        if not validate_size(len(data)):
            self._send_error(413, f"File too large. Max: {settings.max_file_size_mb} MB")
            return
            
        ext = original_name.split(".")[-1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        
        try:
            save_image(filename, data)
            
            image_id = self.repo.create(
                filename=filename,
                original_name=original_name,
                size=len(data),
                file_type=ext
            )
        except Exception as e:
            logger.error("Error creating or saving image", e)
            delete_image(filename)
        
        self._send_json(201, {
            "id": image_id,
            "filename": filename,
            "url": f"/images/{filename}"
            }
        )
    
        
    def delete_image(self):
        filename = self.path.split("/")[-1]
        
        # delete in DB
        deleted = self.repo.delete_by_filename(filename)
        if not deleted:
            self._send_error(404, "Image not found")
            return
        
        # delete in filesytem
        if not delete_image(filename):
            self._send_error(404, "Image not found")
            return
        
        self._send_json(204, {})
      
        
    def do_GET(self):
        logger.info(f"Received GET request for {self.path}")
        
        parts = self._path_parts()
        
        if parts[0] == "images":
            if len(parts) >= 2:
                self.get_image()
            else:
                self.get_images()
                
        

    def do_POST(self):
        logger.info(f"Received POST request for {self.path}")
        
        parts = self._path_parts()
        
        if parts[0] == "upload":
            self.create_image()
            
    
    def do_DELETE(self):
        logger.info(f"Received DELETE request for {self.path}")
        
        parts = self._path_parts()

        
        if parts[0] == "images" and len(parts) >= 2:
            self.delete_image()
            
    
if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), ImageAPIServer)
    
    try:
        print("Сервер запущено...")
        server.serve_forever()
    except Exception as e:
        print(f"Трапилась помилка: {e}")