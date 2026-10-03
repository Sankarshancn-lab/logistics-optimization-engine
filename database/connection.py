from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker


PROJECT_ROOT = Path.cwd().resolve()

DATABASE_FILE = PROJECT_ROOT / "logistics_routing.db"

DATABASE_URL = f"sqlite:///{DATABASE_FILE}"


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """
    Enable SQLite foreign-key enforcement for every connection.
    """
    cursor = dbapi_connection.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    finally:
        cursor.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_session():
    """
    Create and return a database session.

    The caller is responsible for closing the session.
    """
    return SessionLocal()
