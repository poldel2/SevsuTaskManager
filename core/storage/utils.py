from typing import Set
import magic
import os

ALLOWED_IMAGE_TYPES: Set[str] = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp'
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_file_type(file_content: bytes, allowed_types: Set[str] = ALLOWED_IMAGE_TYPES) -> bool:
    """Проверяет тип файла по его содержимому"""
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file_content)
    return file_type in allowed_types

def validate_file_size(file_size: int, max_size: int = MAX_FILE_SIZE) -> bool:
    """Проверяет размер файла"""
    return file_size <= max_size

def get_safe_filename(filename: str) -> str:
    """Генерирует безопасное имя файла"""
    import uuid
    ext = os.path.splitext(filename)[1].lower()
    return f"{uuid.uuid4()}{ext}"