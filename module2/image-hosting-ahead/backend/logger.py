import logging
from pathlib import Path

from config import settings

logs_dir = Path(settings.logs_dir)
logs_dir.mkdir(parents=True, exist_ok=True)
log_file = logs_dir / "app.log"

formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler],
)

logger = logging.getLogger(__name__)