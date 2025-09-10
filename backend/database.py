import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")

_engine = None
_Session = None


class Base(DeclarativeBase):
	pass


def init_engine_and_session() -> None:
	global _engine, _Session
	if _engine is None:
		_engine = create_engine(DATABASE_URL, echo=False, future=True)
		_Session = scoped_session(sessionmaker(bind=_engine, autoflush=False, autocommit=False))
		Base.metadata.create_all(_engine)


@contextmanager
def session_scope() -> Iterator[scoped_session]:
	if _Session is None:
		raise RuntimeError("Database not initialized. Call init_engine_and_session() first.")
	session = _Session()
	try:
		yield session
		session.commit()
	except Exception:
		session.rollback()
		raise
	finally:
		session.close()
