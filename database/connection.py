import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config.settings import settings


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = psycopg2.connect(settings.database_url)
        yield conn
    finally:
        if conn:
            conn.close()


@contextmanager
def get_db_cursor():
    """Context manager for database cursors"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                yield cursor
                conn.commit()
            except Exception:
                conn.rollback()
                raise

