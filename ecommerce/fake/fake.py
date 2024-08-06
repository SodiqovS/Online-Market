import random
from typing import List
from pathlib import Path
import logging
import sys

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ecommerce.image import save_fake_image
from ecommerce.products import models

# Configure logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

# Define the base path for your images
BASE_IMAGE_PATH = Path(__file__).parent


async def create_fake_category(name: str, image_path: Path, database: AsyncSession) -> models.Category:
    logging.debug(f"Opening image at path: {image_path}")
    print(f"Opening image at path: {image_path}")
    with image_path.open("rb") as image_file:
        image = UploadFile(filename=image_path.name, file=image_file)
        image_url = await save_fake_image(image, folder="static/images/categories")

        new_category = models.Category(name=name, image_url=image_url)
        database.add(new_category)
        await database.commit()
        await database.refresh(new_category)
        return new_category


async def create_fake_categories(database: AsyncSession, count: int = 10):
    category_names = ['Electronics', 'Clothing', 'Books', 'Toys', 'Furniture', 'Beauty', 'Sports', 'Automotive',
                      'Garden', 'Grocery']
    image_paths = [
        BASE_IMAGE_PATH / "category1.png",
        BASE_IMAGE_PATH / "category2.png",
    ]

    categories = []
    for i in range(count):
        name = random.choice(category_names) + str(i)
        image_path = random.choice(image_paths)
        logging.debug(f"Creating category with name: {name} and image path: {image_path}")
        print(f"Creating category with name: {name} and image path: {image_path}")
        category = await create_fake_category(name, image_path, database)
        categories.append(category)

    return categories


async def create_fake_product(name: str, quantity: int, description: str, price: int, category_id: int,
                              image_path, database: AsyncSession) -> models.Product:
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

    with image_path.open("rb") as image_file:
        image = UploadFile(filename=image_path.name, file=image_file)
        image_url = await save_fake_image(image, folder="static/images/products")
        new_image = models.Image(product_id=product.id, url=image_url)
        database.add(new_image)

    await database.commit()
    await database.refresh(product, attribute_names=['images', 'category'])

    return product


async def create_fake_products(database: AsyncSession, categories: List[models.Category], count: int = 50):
    product_names = ['Laptop', 'T-Shirt', 'Book', 'Toy Car', 'Sofa', 'Lipstick', 'Basketball', 'Car Tire', 'Lawn Mower',
                     'Cereal']
    image_paths = [
        BASE_IMAGE_PATH / "prod1.png",
        BASE_IMAGE_PATH / "prod2.jpg",
        BASE_IMAGE_PATH / "prod3.png",
        BASE_IMAGE_PATH / "prod4.png",
        BASE_IMAGE_PATH / "prod5.jpg",
        BASE_IMAGE_PATH / "prod6.jpg"
    ]

    products = []
    for i in range(count):
        name = random.choice(product_names) + str(i)
        quantity = random.randint(1, 100)
        description = f"Description for {name}"
        price = random.randint(10, 1000)
        category = random.choice(categories)
        image_path = random.choice(image_paths)
        product = await create_fake_product(name, quantity, description, price, category.id, image_path, database)
        products.append(product)

    return products


async def create_test_data(database: AsyncSession):
    categories = await create_fake_categories(database, count=10)
    products = await create_fake_products(database, categories=categories, count=50)
    return categories, products
