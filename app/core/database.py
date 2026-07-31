from typing import Generator
from contextlib import contextmanager
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings


def create_engine_with_settings() -> Engine:
    """
    Создает движок SQLAlchemy с настройками из конфигурации

    Returns:
        Engine: Движок SQLAlchemy
    """
    engine = create_engine(
        settings.database_url,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.debug,
        echo_pool=settings.debug,
        connect_args=(
            {
                "connect_timeout": 10,
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
            }
            if settings.enviroment == "production"
            else {}
        ),
    )

    return engine


engine = create_engine_with_settings()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Генератор сессий для использования в FastAPI через Depends

    Returns:
        Generator[Session, None, None]: Генератор сессий SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Контекстный менеджер для получения сессии БД

    Returns:
        Generator[Session, None, None]: Генератор сессий SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Получить новую сессию БД (вручную управлять закрытием)

    Returns:
        Session: Сессия SQLAlchemy
    """
    return SessionLocal()


@event.listens_for(engine, "connect")
def set_postgres_timezone(dbapi_connection, connection_record):
    """
    Устанавливаем часовой пояс UTC для соединения
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("SET timezone = 'UTC';")
    cursor.close()


@event.listens_for(engine, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    """
    Проверяем соединение перед использованием (для Pool)
    """
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except Exception:
        raise
    finally:
        cursor.close()
