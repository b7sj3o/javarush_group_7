

import os

from config import settings

def save_image(filename: str, data: bytes):
    os.makedirs(settings.images_dir, exist_ok=True)
    
    with open(os.path.join(settings.images_dir, filename), "wb") as f:
        f.write(data)
        

def image_exists(filename) -> bool:
    return os.path.exists(os.path.join(settings.images_dir, filename))


def delete_image(filename) -> bool:
    """
    returns True if image was successfully deleted, False otherwise
    """
    
    try:
        os.remove(os.path.join(settings.images_dir, filename))
        return True
    except FileNotFoundError:
        return False        