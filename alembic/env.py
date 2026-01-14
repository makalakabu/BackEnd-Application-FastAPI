from logging.config import fileConfig
import os
import sys

from dotenv import load_dotenv
load_dotenv()
from core.config import DATABASE_URL


from sqlalchemy import create_engine, pool
from alembic import context

sys.path.append(os.path.abspath(os.getcwd()))

from db.session import DATABASE_URL
from db.db_base import Base

from models.user import User
from models.tweet import Tweet
from models.follow import Follow

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
