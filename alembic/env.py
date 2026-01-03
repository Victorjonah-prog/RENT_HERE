from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os


# this is the Alembic Config object
config = context.config

# Get database credentials from environment variables (set by docker-compose)
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'renthere')
DB_HOST = os.environ.get('DB_HOST', 'renthere_db')
DB_PORT = os.environ.get('DB_PORT', '3306')
DB_DATABASE = os.environ.get('DB_DATABASE', 'renthere_db')

# Construct the database URL
DATABASE_URL = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'
config.set_main_option('sqlalchemy.url', DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
from app.models.base import Base 

from app.models.apartments_model import Apartments
from app.models.landlords_model import Landlords
from app.models.tenants_model import Tenants
from app.models.users_model import Users

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    from sqlalchemy import create_engine
    
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
