from __future__ import with_statement

from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

from ecommerce import config as config_env
from ecommerce.db import Base  # noqa
from ecommerce.user.models import User  # noqa
from ecommerce.products.models import Category, Product, Image  # noqa
from ecommerce.orders.models import Order, OrderDetails  # noqa
from ecommerce.cart.models import Cart, CartItems  # noqa

target_metadata = Base.metadata


def get_url():
    db_user = config_env.DATABASE_USERNAME
    db_password = config_env.DATABASE_PASSWORD
    db_host = config_env.DATABASE_HOST
    db_name = config_env.DATABASE_NAME
    return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}/{db_name}"


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_async_engine(
        get_url(),
        poolclass=NullPool,
    )

    async def async_run_migrations():
        # connectable is an instance of AsyncEngine
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

    import asyncio
    asyncio.run(async_run_migrations())


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
