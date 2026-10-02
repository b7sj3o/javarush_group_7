import http.server
import os
import uuid
import cgi
import datetime

# ============================
# Налаштування
# ============================
HOST = "localhost"
PORT = 8000

IMAGES_DIR = "images"
LOGS_DIR = "logs"
LOG_FILE = os.path.join(LOGS_DIR, "app.log")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ в байтах


# ============================
# Логування
# ============================
def log(action: str, message: str):
    """Записує повідомлення в лог-файл і виводить у термінал."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {action}: {message}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

    print(entry, end="")


# ============================
# Генерація унікального імені
# ============================
def generate_filename(original_name: str) -> str:
    """
    Генерує унікальне ім'я файлу на основі UUID.
    Зберігає оригінальне розширення.

    Приклад: photo.jpg -> a3f1b2c4.jpg
    """
    ext = os.path.splitext(original_name)[1].lower()
    unique_name = uuid.uuid4().hex[:8]  # перші 8 символів UUID
    return f"{unique_name}{ext}"


# ============================
# Обробник HTTP-запитів
# ============================
class ImageServerHandler(http.server.BaseHTTPRequestHandler):

    # --- GET / ---
    def handle_home(self):
        """Головна сторінка сервісу."""
        html = """
        <!DOCTYPE html>
        <html lang="uk">
        <head>
            <meta charset="UTF-8">
            <title>Сервер зображень</title>
        </head>
        <body>
            <h1>Ласкаво просимо до сервера зображень!</h1>
            <p>Цей сервіс дозволяє завантажувати та переглядати зображення.</p>
            <ul>
                <li><a href="/upload">Завантажити зображення</a></li>
                <li><a href="/images/">Переглянути всі зображення</a></li>
            </ul>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    # --- GET /upload ---
    def handle_upload_page(self):
        """Сторінка з формою для завантаження."""
        html = """
        <!DOCTYPE html>
        <html lang="uk">
        <head>
            <meta charset="UTF-8">
            <title>Завантаження зображення</title>
        </head>
        <body>
            <h1>Завантаження зображення</h1>
            <form method="POST" action="/upload" enctype="multipart/form-data">
                <input type="file" name="image" accept=".jpg,.jpeg,.png,.gif">
                <button type="submit">Завантажити</button>
            </form>
            <p>Підтримуються формати: JPG, PNG, GIF. Максимальний розмір: 5 МБ.</p>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    # --- POST /upload ---
    def handle_upload(self):
        """Приймає файл від користувача та зберігає його."""

        # Читаємо multipart/form-data
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={"REQUEST_METHOD": "POST"},
        )

        # Перевіряємо що поле "image" є у формі
        if "image" not in form:
            self.send_error_response(400, "Поле 'image' відсутнє в запиті.")
            log("Помилка", "Запит без поля 'image'")
            return

        file_item = form["image"]
        original_name = file_item.filename

        # Перевірка розширення
        ext = os.path.splitext(original_name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            self.send_error_response(400, f"Непідтримуваний формат файлу ({original_name}).")
            log("Помилка", f"непідтримуваний формат файлу ({original_name})")
            return

        # Читаємо вміст файлу
        file_data = file_item.file.read()

        # Перевірка розміру
        if len(file_data) > MAX_FILE_SIZE:
            self.send_error_response(400, f"Файл завеликий. Максимум 5 МБ, отримано {len(file_data) // 1024} КБ.")
            log("Помилка", f"файл {original_name} завеликий ({len(file_data)} байт)")
            return

        # Генеруємо унікальне ім'я та зберігаємо файл
        new_filename = generate_filename(original_name)
        save_path = os.path.join(IMAGES_DIR, new_filename)

        with open(save_path, "wb") as f:
            f.write(file_data)

        log("Успіх", f"зображення {new_filename} завантажено (оригінал: {original_name})")

        # Повертаємо користувачу посилання на файл
        image_url = f"/images/{new_filename}"
        html = f"""
        <!DOCTYPE html>
        <html lang="uk">
        <head>
            <meta charset="UTF-8">
            <title>Успішно завантажено</title>
        </head>
        <body>
            <h1>Зображення успішно завантажено!</h1>
            <p>Посилання на файл: <a href="{image_url}">{image_url}</a></p>
            <img src="{image_url}" style="max-width: 400px;">
            <br><br>
            <a href="/upload">Завантажити ще одне</a>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    # --- GET /images/ ---
    def handle_images_list(self):
        """Показує список усіх завантажених зображень."""
        files = os.listdir(IMAGES_DIR)
        images = [f for f in files if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS]

        if not images:
            items_html = "<p>Зображень поки немає.</p>"
        else:
            items_html = "<ul>"
            for img in images:
                items_html += f'<li><a href="/images/{img}">{img}</a></li>'
            items_html += "</ul>"

        html = f"""
        <!DOCTYPE html>
        <html lang="uk">
        <head>
            <meta charset="UTF-8">
            <title>Всі зображення</title>
        </head>
        <body>
            <h1>Завантажені зображення</h1>
            {items_html}
            <a href="/">На головну</a>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    # --- GET /images/<filename> ---
    def handle_image_file(self, filename: str):
        """Повертає конкретний файл зображення."""
        file_path = os.path.join(IMAGES_DIR, filename)

        if not os.path.exists(file_path):
            self.send_error_response(404, f"Файл '{filename}' не знайдено.")
            log("Помилка", f"файл {filename} не знайдено")
            return

        # Визначаємо MIME-тип
        ext = os.path.splitext(filename)[1].lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
        }
        mime = mime_types.get(ext, "application/octet-stream")

        with open(file_path, "rb") as f:
            data = f.read()

        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ============================
    # Маршрутизація
    # ============================
    def do_GET(self):
        if self.path == "/":
            self.handle_home()
        elif self.path == "/upload":
            self.handle_upload_page()
        elif self.path == "/images/" or self.path == "/images":
            self.handle_images_list()
        elif self.path.startswith("/images/"):
            filename = self.path[len("/images/"):]
            self.handle_image_file(filename)
        else:
            self.send_error_response(404, "Сторінку не знайдено.")

    def do_POST(self):
        if self.path == "/upload":
            self.handle_upload()
        else:
            self.send_error_response(404, "Маршрут не знайдено.")

    # ============================
    # Допоміжні методи
    # ============================
    def send_error_response(self, code: int, message: str):
        """Відправляє HTML-відповідь з помилкою."""
        html = f"""
        <!DOCTYPE html>
        <html lang="uk">
        <head><meta charset="UTF-8"><title>Помилка</title></head>
        <body>
            <h1>Помилка {code}</h1>
            <p>{message}</p>
            <a href="/">На головну</a>
        </body>
        </html>
        """
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        """Вимикаємо стандартний лог http.server (він зайвий)."""
        pass


# ============================
# Запуск сервера
# ============================
if __name__ == "__main__":
    # Створюємо директорії якщо не існують
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    log("Старт", f"сервер запущено на http://{HOST}:{PORT}")

    server = http.server.HTTPServer((HOST, PORT), ImageServerHandler)

    try:
        print(f"Сервер працює: http://{HOST}:{PORT}")
        print("Зупинити: Ctrl+C\n")
        server.serve_forever()
    except KeyboardInterrupt:
        log("Стоп", "сервер зупинено вручну")
        print("\nСервер зупинено.")
