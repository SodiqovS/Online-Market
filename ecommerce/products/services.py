from async_lru import alru_cache
from sqlalchemy import select, join
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from . import models
from .models import Category
from ecommerce.image import save_image

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from ecommerce.orders.models import OrderDetails
from ecommerce.products.models import Product


async def create_new_category(name, image, database: AsyncSession) -> models.Category:
    image_url = await save_image(image, folder="static/images/categories")

    new_category = models.Category(name=name, image_url=image_url)
    database.add(new_category)
    await database.commit()
    await database.refresh(new_category)
    return new_category


@alru_cache
async def get_all_categories(database: AsyncSession):
    result = await database.execute(select(models.Category))
    categories = result.scalars().all()
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

    for image in images:
        image_url = await save_image(image, folder="static/images/products")
        new_image = models.Image(product_id=product.id, url=image_url)
        database.add(new_image)

    await database.commit()
    await database.refresh(product, attribute_names=['images', 'category'])

    return product


async def get_best_selling_products(database: AsyncSession, limit: int = 10):
    ...


async def get_product_by_id(product_id: int, database: AsyncSession):
    product = await database.get(models.Product, product_id)

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return await product.load_related(database=database)


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
    await database.refresh(product, attribute_names=["images", "category"])
    return product


async def delete_product(product_id: int, database: AsyncSession):
    product = await database.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    await database.delete(product)
    await database.commit()
