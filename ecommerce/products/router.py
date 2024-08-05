from typing import List, Optional

from async_lru import alru_cache

from fastapi import APIRouter, Depends, status, Response, HTTPException, UploadFile, File, Form
from fastapi.params import Query

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ecommerce import db
from . import schema, services, validator
from ecommerce.auth.jwt import get_current_admin
from ecommerce.user.schema import User
from .models import Product
from .services import get_best_selling_products
from ..custom_page import CustomPage

router = APIRouter(
    tags=['Products'],
    prefix='/products'
)


# @router.get('/category/fake')
# async def fake_category(database: AsyncSession = Depends(db.get_db)):
#     fake = Faker()
#     for _ in range(10):
#         new_category = Category(name=fake.name(), image_url=fake.url())
#         database.add(new_category)
#         await database.commit()
#         await database.refresh(new_category)
#     return {'message': 'Category fake data'}


@router.post('/category', status_code=status.HTTP_201_CREATED)
async def create_category(name: str = Form(...),
                          image: UploadFile = File(...),
                          database: AsyncSession = Depends(db.get_db),
                          current_admin: User = Depends(get_current_admin)):
    new_category = await services.create_new_category(name, image, database)
    return new_category


@router.get('/category', response_model=List[schema.Category])
async def get_all_categories(database: AsyncSession = Depends(db.get_db)):
    return await services.get_all_categories(database)


@router.get('/category/{category_id}', response_model=schema.Category)
async def get_category_by_id(category_id: int, database: AsyncSession = Depends(db.get_db)):
    return await services.get_category_by_id(category_id, database)


@router.delete('/category/{category_id}')
async def delete_category_by_id(category_id: int,
                                database: AsyncSession = Depends(db.get_db),
                                current_admin: User = Depends(get_current_admin)):
    await services.delete_category_by_id(category_id, database)
    return {'message': 'Category deleted'}


# @router.get('/fake')
# async def fake_products(database: AsyncSession = Depends(db.get_db)):
#     fake = Faker()
#     try:
#         for _ in range(100):
#             new_product = Product(
#                 name=fake.name(),
#                 quantity=fake.random_int(100, 1000),
#                 description=fake.text(max_nb_chars=100, ext_word_list=['abc', 'def', 'ghi', 'jkl']),
#                 price=fake.random_int(1000, 10000000),
#                 category_id=fake.random_int(1, 10),
#             )
#             database.add(new_product)
#
#         await database.commit()
#     except:
#         return HTTPException(status_code=400, detail='Something went wrong')
#
#     return {'message': 'Fake successfully'}


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schema.Product)
async def create_product(name: str = Form(...),
                         quantity: int = Form(...),
                         description: str = Form(...),
                         price: int = Form(...),
                         category_id: int = Form(...),
                         images: List[UploadFile] = File(...),
                         database: AsyncSession = Depends(db.get_db),
                         current_admin: User = Depends(get_current_admin)):
    category = await validator.verify_category_exist(category_id, database)
    if not category:
        raise HTTPException(
            status_code=400,
            detail="You have provided an invalid category ID.",
        )

    product = await services.create_product(name, quantity, description, price, category_id, images, database)

    return product


@router.get("/best-selling-products", )
async def best_selling_products(limit: int = 10, database: AsyncSession = Depends(db.get_db)):
    products = await get_best_selling_products(database, limit)
    return products


@router.get('/{product_id}', response_model=schema.Product)
async def get_product_by_id(product_id: int, database: AsyncSession = Depends(db.get_db)):
    return await services.get_product_by_id(product_id, database)


@alru_cache
@router.get('/', response_model=CustomPage[schema.Product])
async def get_all_products(s: Optional[str] = None,
                           categories: Optional[List[int]] = Query(default=[]),
                           sort_by: Optional[str] = 'id',
                           sort_order: Optional[str] = 'desc',
                           database: AsyncSession = Depends(db.get_db)):
    query = select(Product)

    # Search filter
    if s:
        search_filter = or_(
            Product.name.ilike(f"%{s}%"),
            Product.description.ilike(f"%{s}%")
        )
        query = query.where(search_filter)

    # Categories filter
    if categories:
        query = query.where(Product.category_id.in_(categories))

    # Sorting
    sort_order_func = {
        'asc': lambda col: col.asc(),
        'desc': lambda col: col.desc()
    }

    sort_columns = {
        'id': Product.id,
        'name': Product.name,
        'price': Product.price
    }

    if sort_by in sort_columns and sort_order in sort_order_func:
        query = query.order_by(sort_order_func[sort_order](sort_columns[sort_by]))

    return await paginate(database, query)


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
