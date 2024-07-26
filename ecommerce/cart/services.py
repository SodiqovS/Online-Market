from fastapi import HTTPException, status, Depends
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ecommerce.products.models import Product
from .models import Cart, CartItems
from .schema import ShowCart


async def add_to_cart(product_id: int, quantity: int, current_user, database: AsyncSession):
    product_info = await database.execute(select(Product).where(Product.id == product_id))
    product_info = product_info.scalar()
    if not product_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if product_info.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item out of stock")

    cart_info = await database.execute(select(Cart).filter(Cart.user_id == current_user.id))
    cart_info = cart_info.scalar()
    if not cart_info:
        new_cart = Cart(user_id=current_user.id)
        database.add(new_cart)
        await database.commit()
        await database.refresh(new_cart)
        await add_items(new_cart.id, product_info.id, quantity, database)
    else:
        await add_items(cart_info.id, product_info.id, quantity, database)
    return {"status": "Item added to cart"}


async def add_items(cart_id: int, product_id: int, quantity: int, database: AsyncSession):
    cart_items = CartItems(cart_id=cart_id, product_id=product_id, quantity=quantity)
    database.add(cart_items)
    await database.commit()
    await database.refresh(cart_items)
    return {'detail': 'Item added to cart'}


async def get_all_items(current_user, database: AsyncSession) -> ShowCart:
    result = await database.execute(
        select(Cart)
        .filter(Cart.user_id == current_user.id)
    )
    cart = result.scalar()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart is empty")

    return await cart.load_related(database=database)


async def remove_cart_item(cart_item_id: int, current_user, database: AsyncSession):
    result = await database.execute(
        select(Cart)
        .filter(Cart.user_id == current_user.id)
    )
    cart = result.scalar()

    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

    cart_item = await database.execute(select(CartItems).filter(
        and_(CartItems.id == cart_item_id, CartItems.cart_id == cart.id)
    ))
    cart_item = cart_item.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    await database.delete(cart_item)
    await database.commit()
    return {"detail": "Cart item successfully removed"}
