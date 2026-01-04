import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DEFAULT_DB_NAME = "pal_budget.db"


def _resolve_database_path() -> str:
    """Resolve an absolute path for the SQLite database.

    Priorities:
    1. Explicit DATABASE_PATH env.
    2. DATABASE_DIR env or the Render persistent disk (/app/data).
    3. Project working directory (local development).
    """
    env_path = os.getenv("DATABASE_PATH")
    if env_path:
        db_path = Path(env_path)
    else:
        data_dir_candidates = [
            os.getenv("DATABASE_DIR"),
            "/app/data",
            os.getcwd(),
        ]
        db_path = None
        for folder in data_dir_candidates:
            if not folder:
                continue
            folder_path = Path(folder).expanduser()
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
            except Exception:
                continue
            if folder_path.is_dir():
                db_path = folder_path / DEFAULT_DB_NAME
                break
        if db_path is None:
            db_path = Path(DEFAULT_DB_NAME)

    if db_path.parent:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    return str(db_path.resolve())


DATABASE_PATH = _resolve_database_path()
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
