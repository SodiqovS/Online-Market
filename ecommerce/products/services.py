from typing import List, Optional

from sqlalchemy import desc, asc
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from . import models, schema


async def create_new_category(request: schema.CategoryCreate, database: Session) -> models.Category:
    new_category = models.Category(name=request.name)
    database.add(new_category)
    database.commit()
    database.refresh(new_category)
    return new_category


async def get_all_categories(database: Session) -> List[models.Category]:
    categories = database.query(models.Category).all()
    return categories


async def get_category_by_id(category_id: int, database: Session) -> models.Category:
    category_info = database.query(models.Category).filter(models.Category.id == category_id).first()
    if not category_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Not Found!")
    return category_info


async def delete_category_by_id(category_id: int, database: Session):
    database.query(models.Category).filter(models.Category.id == category_id).delete()
    database.commit()


async def create_new_product(request: schema.ProductCreate, database: Session) -> models.Product:
    new_product = models.Product(
        name=request.name,
        quantity=request.quantity,
        description=request.description,
        price=request.price,
        category_id=request.category_id
    )
    database.add(new_product)
    database.commit()
    database.refresh(new_product)

    database.commit()
    return new_product


async def create_new_image(product_id: int, image_url: str, database: Session) -> models.Image:
    new_image = models.Image(product_id=product_id, url=image_url)
    database.add(new_image)
    database.commit()
    database.refresh(new_image)
    return new_image


async def get_product_by_id(product_id: int, database: Session) -> Optional[models.Product]:
    product = database.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


async def get_all_products(database: Session,
                           name: Optional[str] = None,
                           category_id: Optional[int] = None,
                           min_price: Optional[float] = None,
                           max_price: Optional[float] = None,
                           order_by: Optional[str] = 'id',
                           order_direction: Optional[str] = 'asc',
                           limit: int = 10,
                           skip: int = 0):
    query = database.query(models.Product)

    if name:
        query = query.filter(models.Product.name.ilike(f"%{name}%"))
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if min_price:
        query = query.filter(models.Product.price >= min_price)
    if max_price:
        query = query.filter(models.Product.price <= max_price)

    total_products = query.count()

    if order_by:
        if order_direction == 'desc':
            query = query.order_by(desc(getattr(models.Product, order_by)))
        else:
            query = query.order_by(asc(getattr(models.Product, order_by)))

    products = query.offset(skip).limit(limit).all()
    total_pages = (total_products // limit) + (1 if total_products % limit > 0 else 0)
    current_page = (skip // limit) + 1

    return {
        "products": products,
        "total_products": total_products,
        "total_pages": total_pages,
        "current_page": current_page
    }


async def update_product(product_id: int, request, database: Session) -> models.Product:
    product = database.query(models.Product).filter(models.Product.id == product_id).first()
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

    database.commit()
    database.refresh(product)
    return product


async def delete_product(product_id: int, database: Session):
    product = database.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    database.delete(product)
    database.commit()
