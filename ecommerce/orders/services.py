from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import  AsyncSession

from ecommerce.cart.models import Cart, CartItems
from ecommerce.orders.models import Order, OrderDetails


async def initiate_order(current_user, database: AsyncSession) -> Order:
    cart = await database.execute(Cart).filter(Cart.user_id == current_user.id).first()

    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Cart found for current user!")

    cart_items_objects = await database.execute(CartItems).filter(CartItems.cart_id == cart.id).all()
    if not cart_items_objects:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Items found in Cart!")

    total_amount: int = 0
    for item in cart_items_objects:
        product = item.products
        if product.quantity < item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Not enough quantity for product {product.name}. Available: {product.quantity}, Requested: {item.quantity}")
        total_amount += product.price * item.quantity

    new_order = Order(order_amount=total_amount,
                      shipping_address=current_user.address,
                      customer_id=current_user.id)
    database.add(new_order)
    database.commit()
    database.refresh(new_order)

    bulk_order_details_objects = list()
    for item in cart_items_objects:
        product = item.products
        product.quantity -= item.quantity
        database.commit()

        new_order_details = OrderDetails(order_id=new_order.id,
                                         product_id=item.products.id,
                                         quantity=item.quantity)
        bulk_order_details_objects.append(new_order_details)

    database.bulk_save_objects(bulk_order_details_objects)
    database.commit()

    # Savatdagi mahsulotlarni tozalash
    await database.execute(CartItems).filter(CartItems.cart_id == cart.id).delete()
    database.commit()

    return new_order


async def get_order_listing(current_user, database) -> List[Order]:
    orders = await database.execute(Order).filter(Order.customer_id == current_user.id).all()
    return orders


async def get_all_orders(database) -> List[Order]:
    orders = await database.execute(Order).all()
    return orders


