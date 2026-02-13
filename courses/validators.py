import os
from django.core.exceptions import ValidationError

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg"}
MAX_UPLOAD_MB = 10

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

def validate_file_size(value):
    max_bytes = MAX_UPLOAD_MB * 1024 * 1024
    if value.size > max_bytes:
        raise ValidationError(f"File too large. Max size is {MAX_UPLOAD_MB}MB.")
