"""
Engine / session management.

Best practice: one Engine per process (it owns a connection pool), created
lazily so importing this module doesn't require a live DB (important for
unit tests that never touch the database).
"""

from contextlib import contextmanager
from functools import lru_cache
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.config import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(
        settings.sqlalchemy_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # avoids "server closed the connection unexpectedly" errors
        future=True,
    )


@lru_cache
def get_sessionmaker() -> sessionmaker:
    return sessionmaker(bind=get_engine(), expire_on_commit=False, future=True)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional scope: commits on success, rolls back on error."""
    session = get_sessionmaker()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
