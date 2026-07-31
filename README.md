# Сервис бронирования переговорных комнат

Веб-сервис для автоматизации бронирования переговорных комнат в коворкинге. Тестовое задание для поступления на курс `Python` от команды **ШИФТ**.

## Быстрый старт

### Docker
Склонировать переменные окружения:
```bash
cp .env.example .env
```
Развернуть контейнеры:
```bash
docker-compose up --build
```
> При первом запуске автоматически применяются миграции и загружаются тестовые данные.


### Локальный запуск
Запустить контейнер с БД:
```bash
docker-compose up -d db
```
Склонировать переменные окружения:
```bash
cp .env.example .env
```
Установить зависимости:
```bash
poetry install
```
Накатить миграцию на БД:
```bash
poetry run alembic upgrade head
```
Наполнить БД тестовыми данными:
```bash
python -m app.scripts.seed
```
Запустить сервис:
```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Тесты
```bash
poetry run pytest
```

## API
Документация доступна после запуска:

- Swagger: http://localhost:8000/api/docs

- ReDoc: http://localhost:8000/api/redoc


### Аутентификация
`POST /api/v1/auth/register` - Регистрация нового сотрудника
`POST /api/v1/auth/login` - Получение JWT токена

*Пример запроса на логин:*
```json
{
"username": "employee@example.com",
"password": "password123"
}
```
*Ответ:*
```json
{
"access_token": "eyJhbGciOiJIUzI1NiIs...",
"token_type": "bearer",
"expires_in": 1800,
"user_id": 1,
"role": "employee"
}
```

> Примечание: Токен передается в заголовке: Authorization: Bearer <token>

### Пользователи
`GET /api/v1/users/me` - Информация о себе (все)

`PUT /api/v1/users/me` - Обновить свои данные (все)

`GET /api/v1/users/` - Список пользователей (админ)

`POST /api/v1/users/` - Создать пользователя (админ)

`GET /api/v1/users/{user_id}` - Получить пользователя (админ)

`PUT /api/v1/users/{user_id}` - Обновить пользователя (админ)

`DELETE /api/v1/users/{user_id}` - Удалить пользователя (админ)

### Комнаты
`GET /api/v1/rooms/` - Список комнат (все)

`GET /api/v1/rooms/{room_id}` - Информация о комнате (все)

`GET /api/v1/rooms/{room_id}/availability` - Доступные слоты на дату (все)

`POST /api/v1/rooms/` - Создать комнату (админ)

`PUT /api/v1/rooms/{room_id}` - Обновить комнату (админ)

`DELETE /api/v1/rooms/{room_id}` - Удалить комнату (админ)

> Примечание: Параметры availability: ?date=YYYY-MM-DD

### Временные слоты
`GET /api/v1/time-slots/rooms/{room_id}` - Список слотов комнаты (все)

`POST /api/v1/time-slots/` - Создать слот (админ)

`PUT /api/v1/time-slots/{slot_id}` - Обновить слот (админ)

`DELETE /api/v1/time-slots/{slot_id}` - Удалить слот (админ)

### Бронирования
`GET /api/v1/bookings/my` - Мои бронирования (все)

`GET /api/v1/bookings/my/history` - История бронирований (все)

`POST /api/v1/bookings/` - Создать бронирование (все)

`GET /api/v1/bookings/{booking_id}` - Получить бронирование (все)

`PUT /api/v1/bookings/{booking_id}` - Обновить бронирование (только автор)

`DELETE /api/v1/bookings/{booking_id}` - Отменить бронирование (автор или админ)

`GET /api/v1/bookings/admin/all` - Все бронирования (админ)

### Права доступа
> **Сотрудник**: просмотр комнат и слотов, создание/отмена своих бронирований

> **Администратор**: все права сотрудника + управление комнатами/слотами/пользователями, отмена любых бронирований

### Тестовые пользователи
*Сотрудник:* `alice / Alice123`

*Сотрудник:* `bob / Bob123`

*Сотрудник:* `charlie / Charlie123`

*Администратор:* `admin / Admin123`

