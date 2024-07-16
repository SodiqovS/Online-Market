from typing import List, Optional

from fastapi import APIRouter, Depends, status, Response, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session

from ecommerce import db
from . import schema, services, validator
from ecommerce.auth.jwt import get_current_admin
from ecommerce.user.schema import User

router = APIRouter(
    tags=['Products'],
    prefix='/products'
)


@router.post('/category', status_code=status.HTTP_201_CREATED)
async def create_category(request: schema.CategoryCreate,
                          database: Session = Depends(db.get_db),
                          current_admin: User = Depends(get_current_admin)):
    new_category = await services.create_new_category(request, database)
    return new_category


@router.get('/category', response_model=List[schema.Category])
async def get_all_categories(database: Session = Depends(db.get_db)):
    return await services.get_all_categories(database)


@router.get('/category/{category_id}', response_model=schema.Category)
async def get_category_by_id(category_id: int, database: Session = Depends(db.get_db)):
    return await services.get_category_by_id(category_id, database)


@router.delete('/category/{category_id}', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_category_by_id(category_id: int,
                                database: Session = Depends(db.get_db),
                                current_admin: User = Depends(get_current_admin)):
    await services.delete_category_by_id(category_id, database)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schema.Product)
async def create_product(request: schema.ProductCreate, database: Session = Depends(db.get_db),
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
async def get_product_by_id(product_id: int, database: Session = Depends(db.get_db)):
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
                       database: Session = Depends(db.get_db)):
    # Faylni server yoki saqlash xizmati ichida saqlash
    file_location = f"static/images/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Fayl URL manzilini bazaga qo'shish
    image_url = f"/static/images/{file.filename}"
    image = await services.create_new_image(product_id, image_url, database)
    return image


@router.get('/', response_model=schema.ProductPaging)
async def get_all_products(
        name: Optional[str] = Query(None, description="Filter by product name"),
        category_id: Optional[int] = Query(None, description="Filter by category ID"),
        min_price: Optional[float] = Query(None, description="Filter by minimum price"),
        max_price: Optional[float] = Query(None, description="Filter by maximum price"),
        order_by: Optional[str] = Query(None, description="Order by field name"),
        order_direction: Optional[str] = Query('asc', description="Order direction: 'asc' or 'desc'"),
        limit: Optional[int] = Query(default=10, ge=1, description="Number of products to return"),
        skip: Optional[int] = Query(default=0, ge=0, description="Number of products to skip"),
        database: Session = Depends(db.get_db)
):
    result = await services.get_all_products(
        database,
        name=name,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        order_by=order_by,
        order_direction=order_direction,
        limit=limit,
        skip=skip
    )
    return result


@router.patch('/{product_id}', response_model=schema.Product)
async def update_product(product_id: int, request: schema.ProductUpdate,
                         current_admin: User = Depends(get_current_admin),
                         database: Session = Depends(db.get_db)):
    return await services.update_product(product_id, request, database)


@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, current_admin: User = Depends(get_current_admin),
                         database: Session = Depends(db.get_db)):
    await services.delete_product(product_id, database)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
