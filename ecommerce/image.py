import os
import uuid
from fastapi import UploadFile, HTTPException

from ecommerce import config

ALLOWED_IMAGE_FORMATS = ["image/jpeg", "image/png", "image/jpg", "image/gif",
                         "image/svg+xml", "image/bmp", "image/tiff", "image/webp", "image/heif"]
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
BASE_URL = config.BASE_URL

async def save_image(file: UploadFile, folder: str = "static/images") -> str:
    if file.content_type not in ALLOWED_IMAGE_FORMATS:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {file.content_type}")

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail=f"Image size exceeds 10 MB: {file.filename}")

    await file.seek(0)

    os.makedirs(folder, exist_ok=True)

    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_location = os.path.join(folder, unique_filename)

    with open(file_location, "wb+") as file_object:
        file_object.write(contents)

    return f"{BASE_URL}/{folder}/{unique_filename}"
