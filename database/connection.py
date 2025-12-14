import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import OperationalError
from contextlib import contextmanager
from urllib.parse import urlparse, urlunparse

from config.settings import settings


def _replace_host_in_url(url: str, new_host: str) -> str:
    """Return connection URL with host replaced by new_host."""
    parsed = urlparse(url)
    netloc = parsed.netloc

    if "@" in netloc:
        creds, hostport = netloc.rsplit("@", 1)
    else:
        creds, hostport = "", netloc

    if ":" in hostport:
        _, port = hostport.split(":", 1)
        hostport = f"{new_host}:{port}"
    elif hostport:
        hostport = new_host

    new_netloc = f"{creds + '@' if creds else ''}{hostport}"
    return urlunparse(parsed._replace(netloc=new_netloc))


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        try:
            conn = psycopg2.connect(settings.database_url)
        except OperationalError as err:
            if "could not translate host name \"postgres\"" in str(err) and "@postgres" in settings.database_url:
                fallback_url = _replace_host_in_url(settings.database_url, "localhost")
                print("DB host 'postgres' is unreachable, retrying with 'localhost'")
                conn = psycopg2.connect(fallback_url)
            else:
                raise
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

