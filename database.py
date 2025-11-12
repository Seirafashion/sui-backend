from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

from . import config

engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI,
    echo=False,
    future=True,
)

SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
