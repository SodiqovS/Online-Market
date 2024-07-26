from __future__ import annotations

from typing import Any, Sequence

from fastapi import HTTPException, status
from sqlalchemy import select, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ecommerce.cart.models import Cart, CartItems
from ecommerce.orders.models import Order, OrderDetails
from ecommerce.products.models import Product


async def get_cart_items(cart_id: int, database: AsyncSession) -> Sequence[Row[Any] | RowMapping | Any]:
    result = await database.execute(
        select(CartItems)
        .filter(CartItems.cart_id == cart_id)
        .join(Product, CartItems.product_id == Product.id)
        .options(
            joinedload(CartItems.product).joinedload(Product.images),
            joinedload(CartItems.product).joinedload(Product.category),
        )
    )
    cart_items_objects = result.unique().scalars().all()
    for item in cart_items_objects:
        print(item.product)
    return cart_items_objects


async def post_order_details(order_id: int, cart_obj, database: AsyncSession):
    cart_items = await get_cart_items(cart_obj.id, database)
    order_details_list = []
    print('1')
    for item in cart_items:
        print(2)
        order_details = OrderDetails(
            order_id=order_id,
            product_id=item.product.id,
            quantity=item.quantity,
        )
        order_details_list.append(order_details)
    database.add_all(order_details_list)
    await database.commit()


async def delete_cart_items(cart_id: int, database: AsyncSession):
    cart_items = await get_cart_items(cart_id, database)
    for item in cart_items:
        await database.delete(item)
    await database.commit()


async def initiate_order(current_user, database: AsyncSession, shipping_address=""):
    if not current_user.address and not shipping_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Please provide a shipping address"
        )

    cart = await database.execute(
        select(Cart)
        .filter(Cart.user_id == current_user.id)
        .options(
            joinedload(Cart.cart_items).joinedload(CartItems.product)
        )
    )
    cart_obj = cart.scalar()

    if not cart_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart is empty"
        )

    cart_items = await get_cart_items(cart_obj.id, database)
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No items found in cart"
        )

    total_order_amount = sum(item.product.price * item.quantity for item in cart_items)

    order = Order(
        customer_id=current_user.id,
        shipping_address=current_user.address,
        order_amount=total_order_amount,
    )

    database.add(order)
    await database.commit()
    await database.refresh(order, attribute_names=["user_info", "order_details"])
    await post_order_details(order.id, cart_obj, database)

    await delete_cart_items(cart_obj.id, database)

    await database.refresh(order, attribute_names=["user_info", "order_details"])

    return await order.load_related(database)


async def get_order_listing(current_user, database: AsyncSession):
    result = await database.execute(
        select(Order).filter(Order.customer_id == current_user.id))
    orders = result.scalars().all()
    orders = [await order.load_related(database) for order in orders]
    return orders


async def get_all_orders(database: AsyncSession):
    result = await database.execute(select(Order))
    orders = result.scalars().all()
    orders = [await order.load_related(database) for order in orders]
    return orders
