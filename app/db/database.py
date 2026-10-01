from fastapi import Request
from psycopg_pool import ConnectionPool

from app.config import settings


def create_pool() -> ConnectionPool:
    return ConnectionPool(
        conninfo=settings.database_url,
        min_size=2,
        max_size=10,
        open=False,
    )


def get_db(request: Request):
    pool: ConnectionPool = request.app.state.db_pool

    with pool.connection() as connection:
        yield connection