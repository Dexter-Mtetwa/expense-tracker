import psycopg

from app.config import settings


def get_connection():
    return psycopg.connect(settings.database_url)


def get_db():
    connection = get_connection()

    try:
        yield connection
    finally:
        connection.close()
