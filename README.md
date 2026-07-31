# Meeting Room Booking Service

Небольшой сервис для бронирования переговорных комнат на FastAPI.

## Краткое описание

Сервис предоставляет API для управления пользователями, комнатами, временными слотами и бронированиями.

## Требования

- Python 3.10+
- Poetry (рекомендуется) или pip
- Docker & Docker Compose (опционально)

## Переменные окружения

Обязательные переменные:

- `SECRET_KEY` — секрет для подписи JWT

Опционально (если не указан `DATABASE_URL`, собирается из компонентов):

- `DATABASE_URL` или `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `ENVIRONMENT` — `development`/`test`/`production` (по умолчанию `development`)
- `DEBUG` — `true`/`false` (по умолчанию `false`)

Можно положить переменные в `.env` в корне проекта.

## Установка (Poetry)

1. Установите зависимости:

```bash
poetry install
```

2. Установите переменные окружения (пример для PowerShell):

```powershell
$env:SECRET_KEY = "change-me-to-a-strong-secret"
$env:DATABASE_URL = "sqlite:///./data.db"  # или URL к Postgres
$env:ENVIRONMENT = "development"
$env:DEBUG = "1"
```

3. Запустите приложение:

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

После старта документация доступна по `http://localhost:8000/api/docs` (если `DEBUG=true`).

## Быстрый запуск через Docker Compose

```bash
docker-compose up --build
```

## Миграции / инициализация БД

Проект содержит `alembic.ini`. Примените миграции:

```bash
alembic upgrade head
```

Для быстрой проверки в локальной среде можно использовать SQLite (см. `DATABASE_URL`).

## Тесты

```bash
pytest --cov=app
```

## Примеры использования API

Все эндпоинты имеют префикс `/api/v1`.

1) Регистрация пользователя

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/register \
	-H 'Content-Type: application/json' \
	-d '{"username":"jdoe","email":"jdoe@example.com","password":"Password1","full_name":"John Doe"}'
```

Успешный ответ: HTTP 201 с объектом пользователя (без пароля).

2) Логин и получение токена

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
	-H 'Content-Type: application/json' \
	-d '{"username":"jdoe","password":"Password1"}'
```

Пример ответа:

```json
{
	"access_token": "eyJ...",
	"token_type": "bearer",
	"expires_in": 1800,
	"user_id": 1,
	"role": "employee"
}
```

3) Получить список комнат

```bash
curl -s http://localhost:8000/api/v1/rooms \
	-H "Authorization: Bearer <ACCESS_TOKEN>"
```

4) Проверить доступность комнаты на дату

```bash
curl -s "http://localhost:8000/api/v1/rooms/1/availability?date_str=2026-08-01" \
	-H "Authorization: Bearer <ACCESS_TOKEN>"
```

5) Создать бронирование

```bash
curl -s -X POST http://localhost:8000/api/v1/bookings \
	-H 'Content-Type: application/json' \
	-H "Authorization: Bearer <ACCESS_TOKEN>" \
	-d '{"room_id":1,"time_slot_id":2,"date":"2026-08-01","description":"Team sync"}'
```

Пример успешного ответа: HTTP 201 с объектом бронирования.

> Примечание: некоторые операции требуют роли `admin` (создание комнат, слотов, просмотр всех бронирований).

## Полезные ссылки

- Документация (Swagger): `http://localhost:8000/api/docs`
- Тесты: запустите `pytest` для проверки покрытия


