from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError

FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 10  # 10MB

def file_validation(file):
    if not file:
        raise ValidationError("No file selected.")
    
    if isinstance(file, UploadedFile):
        if file.size > FILE_UPLOAD_MAX_MEMORY_SIZE:
            raise ValidationError("File shouldn't be larger than 10MB.")