from typing import List, Optional

from async_lru import alru_cache
from faker import Faker
from fastapi import APIRouter, Depends, status, Response, HTTPException, UploadFile, File, Query
from fastapi_filters import FilterValues, create_filters_from_model
from fastapi_filters.ext.sqlalchemy import apply_filters
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
from sqlalchemy import select
from sqlalchemy.ext.asyncio import  AsyncSession

from ecommerce import db
from . import schema, services, validator
from ecommerce.auth.jwt import get_current_admin
from ecommerce.user.schema import User
from .models import Product, Category
from ..custom_page import CustomPage

router = APIRouter(
    tags=['Products'],
    prefix='/products'
)

#
# @router.get('/category/fake')
# async def fake_category(database: AsyncSession = Depends(db.get_db)):
#     fake = Faker()
#     for _ in range(10):
#         new_category = Category(name=fake.name())
#         database.add(new_category)
#         database.commit()
#         database.refresh(new_category)
#     return {'message': 'Category fake data'}


@router.post('/category', status_code=status.HTTP_201_CREATED)
async def create_category(request: schema.CategoryCreate,
                          database: AsyncSession = Depends(db.get_db),
                          current_admin: User = Depends(get_current_admin)):
    new_category = await services.create_new_category(request, database)
    return new_category


@router.get('/category', response_model=List[schema.Category])
async def get_all_categories(database: AsyncSession = Depends(db.get_db)):
    return await services.get_all_categories(database)


@router.get('/category/{category_id}', response_model=schema.Category)
async def get_category_by_id(category_id: int, database: AsyncSession = Depends(db.get_db)):
    return await services.get_category_by_id(category_id, database)


@router.delete('/category/{category_id}', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_category_by_id(category_id: int,
                                database: AsyncSession = Depends(db.get_db),
                                current_admin: User = Depends(get_current_admin)):
    await services.delete_category_by_id(category_id, database)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# @router.get('/fake')
# async def fake_products(database: AsyncSession = Depends(db.get_db)):
#     fake = Faker()
#     for _ in range(100):
#         new_product = Product(
#             name=fake.name(),
#             quantity=fake.random_int(100, 1000),
#             description=fake.text(max_nb_chars=1000, ext_word_list=['abc', 'def', 'ghi', 'jkl']),
#             price=fake.random_int(1000, 10000000),
#             category_id=fake.random_int(1, 11),
#         )
#         database.add(new_product)
#         database.commit()
#         database.refresh(new_product)
#
#     return {'message': 'Fake successfully'}
#

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schema.Product)
async def create_product(request: schema.ProductCreate, database: AsyncSession = Depends(db.get_db),
                         current_admin: User = Depends(get_current_admin)):
    category = await validator.verify_category_exist(request.category_id, database)
    if not category:
        raise HTTPException(
            status_code=400,
            detail="You have provided an invalid category ID.",
        )

    product = await services.create_new_product(request, database)
    return product


@router.get('/{product_id}', response_model=schema.Product)
async def get_product_by_id(product_id: int, database: AsyncSession = Depends(db.get_db)):
    product = await services.get_product_by_id(product_id, database)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.post('/upload/{product_id}', status_code=status.HTTP_201_CREATED)
async def upload_image(product_id: int, file: UploadFile = File(...),
                       current_admin: User = Depends(get_current_admin),
                       database: AsyncSession = Depends(db.get_db)):
    # Faylni server yoki saqlash xizmati ichida saqlash
    file_location = f"static/images/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Fayl URL manzilini bazaga qo'shish
    image_url = f"/static/images/{file.filename}"
    image = await services.create_new_image(product_id, image_url, database)
    return image


@alru_cache
@router.get('/', response_model=CustomPage[schema.Product])
async def get_all_products(database: AsyncSession = Depends(db.get_db),
                           filters: FilterValues = Depends(create_filters_from_model(schema.ProductBase))):
    query = apply_filters(select(Product), filters)
    return paginate(database, query)


@router.patch('/{product_id}', response_model=schema.Product)
async def update_product(product_id: int, request: schema.ProductUpdate,
                         current_admin: User = Depends(get_current_admin),
                         database: AsyncSession = Depends(db.get_db)):
    return await services.update_product(product_id, request, database)


@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, current_admin: User = Depends(get_current_admin),
                         database: AsyncSession = Depends(db.get_db)):
    await services.delete_product(product_id, database)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
