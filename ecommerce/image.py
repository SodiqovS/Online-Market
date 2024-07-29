import os

from fastapi import UploadFile, HTTPException

ALLOWED_IMAGE_FORMATS = ["image/*", "image/jpeg", "image/png", "image/jpg", "image/gif",
                         "image/svg", "image/bmp", "image/tiff", "image/webp", "image/heif"
                         ]
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


async def save_image(file: UploadFile, folder: str = "static/images") -> str:
    if file.content_type not in ALLOWED_IMAGE_FORMATS:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {file.content_type}")

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail=f"Image size exceeds 10 MB: {file.filename}")

    # Reset the image read pointer
    await file.seek(0)

    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)

    # Save the image
    file_location = os.path.join(folder, file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(contents)

    # Return the image URL
    return f"/{folder}/{file.filename}"
