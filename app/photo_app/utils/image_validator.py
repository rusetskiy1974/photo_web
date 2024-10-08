import os
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError

MAX_FILE_SIZE = 1024 * 1024 * 10  # 10MB

def file_validation(file):
    if not file:
        raise ValidationError("No file selected.")
    
    if isinstance(file, UploadedFile):
        if file.size > MAX_FILE_SIZE:
            raise ValidationError("File shouldn't be larger than 10MB.")
        
def validate_download_file_size(file_path):
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValidationError(f"File '{file_path}' exceeds the maximum size of 10MB.")        