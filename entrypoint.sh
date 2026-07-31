#!/bin/bash
set -e

echo "[ ] Сон 5 секунд на случай если БД ещё не поднялась..."
sleep 5

echo "[ ] Накатываем миграции..."
poetry run alembic upgrade head

echo "[ ] Проверяем наличие тестовых данных..."
if poetry run python -c "
from app.core import SessionLocal
from app.models import UserORM
session = SessionLocal()
exists = session.query(UserORM).first() is not None
exit(0 if exists else 1)
"; then
    echo "(!) Тестовые данные уже есть, пропускаем"
else
    echo "[ ] Загружаем тестовые данные..."
    python -m app.scripts.seed
    echo "[+] Тестовые данные загружены"
fi

echo "[ ] Запуск main:app..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000                   