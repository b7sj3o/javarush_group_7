import logging
from logging.handlers import RotatingFileHandler

from pathlib import Path

from config import settings


logs_dir = Path(settings.logs_dir)
logs_dir.mkdir(exist_ok=True, parents=True)
log_file = logs_dir / "app.log"


formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)



file_handler = RotatingFileHandler(
    filename=log_file, 
    encoding="utf-8",
    maxBytes=10*1024*1024,
    backupCount=5
)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)


logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler]
)

logger = logging.getLogger(__name__)