
from faker import Faker
from fastapi import Depends
from sqlalchemy.ext.asyncio import  AsyncSession

from ecommerce import db
from ecommerce.products.models import Category, Product
# from ecommerce.products.models import Category, Product
from ecommerce.user.models import User


def create_fake_data():
    fake = Faker()
    database = db.get_db()
    for _ in range(100):
        user = User(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number=fake.phone_number(),
            telegram_id=fake.random_int(1000000, 99999999),
            username=fake.user_name(),
            address=fake.address(),
        )
        database.add(user)
        database.commit()
        database.refresh(user)

    for _ in range(10):
        new_category = Category(name=fake.name())
        database.add(new_category)
        database.commit()
        database.refresh(new_category)

    for _ in range(100):
        new_product = Product(
            name=fake.name(),
            quantity=fake.random_int(100, 1000),
            description=fake.english_text(1000),
            price=fake.random_int(1000, 10000000),
            category_id=fake.random_int(1, 11),
        )
        database.add(new_product)
        database.commit()
        database.refresh(new_product)


if __name__ == '__main__':
    create_fake_data()
