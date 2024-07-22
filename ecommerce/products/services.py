from async_lru import alru_cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload

from . import models, schema
from .models import Category


async def create_new_category(request: schema.CategoryCreate, database: AsyncSession) -> models.Category:
    new_category = models.Category(name=request.name)
    database.add(new_category)
    await database.commit()
    await database.refresh(new_category)
    return new_category


@alru_cache
async def get_all_categories(database: AsyncSession):
    result = await database.execute(select(models.Category.id, models.Category.name))
    categories = result.all()
    return categories


async def get_category_by_id(category_id: int, database: AsyncSession):
    category_info = await database.get(Category, category_id)
    if not category_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Not Found!")
    return category_info


async def delete_category_by_id(category_id: int, database: AsyncSession):
    category = await database.get(Category, category_id)
    if category:
        await database.delete(category)
        await database.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Not Found!")


async def create_product(name, quantity, description, price, category_id, images, database):
    product = models.Product(
        name=name,
        quantity=quantity,
        description=description,
        price=price,
        category_id=category_id
    )
    database.add(product)
    await database.commit()
    await database.refresh(product)
    await database.flush()

    ALLOWED_IMAGE_FORMATS = ["image/jpeg", "image/png", "image/gif"]
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB

    # Validate image formats and size
    for image in images:
        if image.content_type not in ALLOWED_IMAGE_FORMATS:
            raise HTTPException(status_code=400, detail=f"Invalid image format: {image.content_type}")

        contents = await image.read()
        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail=f"Image size exceeds 10 MB: {image.filename}")

    # Reset the image read pointer
    for image in images:
        await image.seek(0)

    for image in images:
        file_location = f"static/images/{image.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(image.file.read())

        # Fayl URL manzilini bazaga qo'shish
        image_url = f"/static/images/{image.filename}"

        new_image = models.Image(product_id=product.id, url=image_url)
        database.add(new_image)

    await database.commit()
    await database.refresh(product, attribute_names=['images', 'category'])

    return product


async def get_product_by_id(product_id: int, database: AsyncSession):
    query = select(models.Product).options(
        joinedload(models.Product.images),
        joinedload(models.Product.category)
    ).where(models.Product.id == product_id)

    result = await database.execute(query)
    product = result.scalar()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


async def update_product(product_id: int, request, database: AsyncSession):
    product = database.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if request.name is not None:
        product.name = request.name
    if request.quantity is not None:
        product.quantity = request.quantity
    if request.description is not None:
        product.description = request.description
    if request.price is not None:
        product.price = request.price
    if request.category_id is not None:
        product.category_id = request.category_id

    await database.commit()
    await database.refresh(product)
    return product


async def delete_product(product_id: int, database: AsyncSession):
    product = await database.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    await database.delete(product)
    await database.commit()
