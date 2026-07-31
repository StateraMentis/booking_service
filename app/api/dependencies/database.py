from typing import Generator
from sqlalchemy.orm import Session

from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии базы данных

    Используется в эндпоинтах для доступа к БД
    Сессия автоматически закрывается после завершения запроса

    Yields:
        Session: Сессия SQLAlchemy
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
