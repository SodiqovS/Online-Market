from fastapi import HTTPException, status, Depends
from sqlalchemy import and_
from sqlalchemy.orm import Session

from ecommerce import db
from ecommerce.products.models import Product
from .models import Cart, CartItems
from .schema import ShowCart


async def add_to_cart(product_id: int, quantity, current_user, database: Session = Depends(db.get_db)):
    product_info = database.query(Product).get(product_id)
    if not product_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Not Found !")

    if product_info.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item Out of Stock !")

    cart_info = database.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart_info:
        new_cart = Cart(user_id=current_user.id)
        database.add(new_cart)
        database.commit()
        database.refresh(new_cart)
        await add_items(new_cart.id, product_info.id, quantity, database)
    else:
        await add_items(cart_info.id, product_info.id, quantity, database)
    return {"status": "Item Added to Cart"}


async def add_items(cart_id: int, product_id: int, quantity: int, database: Session = Depends(db.get_db)):
    cart_items = CartItems(cart_id=cart_id, product_id=product_id, quantity=quantity)
    database.add(cart_items)
    database.commit()
    database.refresh(cart_items)

    # product_object = database.query(Product).filter(Product.id == product_id)
    # current_quantity = product_object.first().quantity - 1
    # product_object.update({"quantity": current_quantity})
    # database.commit()
    return {'detail': 'Object Updated'}


async def get_all_items(current_user, database) -> ShowCart:
    cart = database.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data Not Found !")
    return cart


async def remove_cart_item(cart_item_id: int, current_user, database: Session):

    cart = database.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

    cart_item = database.query(CartItems).filter(and_(CartItems.id == cart_item_id, CartItems.cart_id == cart.id)).first()
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    database.delete(cart_item)
    database.commit()

    return {"detail": "Cart item successfully removed"}
