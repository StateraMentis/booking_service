"""
Скрипт для заполнения базы данных тестовыми данными
Запуск: python -m app.scripts.seed
"""

import sys
from datetime import date, time
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.timeslot_repository import TimeSlotRepository
from app.repositories.booking_repository import BookingRepository
from app.models.user import UserRole


def seed_database(db: Session) -> None:
    """
    Заполнить БД тестовыми данными
    """

    user_repo = UserRepository(db)
    room_repo = RoomRepository(db)
    time_slot_repo = TimeSlotRepository(db)
    booking_repo = BookingRepository(db)

    users, total_users = user_repo.get_all(limit=1)
    if total_users > 0:
        print("(!)  База данных уже содержит данные. Пропускаем seeding.")
        return

    print("Начинаем заполнение базы данных тестовыми данными...")

    print("  [ ] Создаем администратора...")
    admin = user_repo.create_user(
        username="admin",
        email="admin@example.com",
        password="Admin123",
        full_name="Администратор Системы",
        role=UserRole.ADMIN,
    )
    print(f"     [+] Администратор создан (ID: {admin.id})")

    print("  [ ] Создаем обычных пользователей...")
    users_data = [
        ("monro", "monro@example.com", "SuperPass15", "Зинаида Монро"),
        ("san", "san@example.com", "SanSan1", "Сан Саныч"),
        ("billi", "bill@example.com", "IamBill", "Билли Морган"),
    ]

    users = []
    for username, email, password, full_name in users_data:
        user = user_repo.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
        )
        users.append(user)
        print(f"     [+] Пользователь {username} создан (ID: {user.id})")

    print("  [ ] Создаем комнаты и временные слоты...")
    rooms_data = [
        (
            "Переговорная А",
            8,
            [
                ("09:00", "11:00"),
                ("11:00", "13:00"),
                ("14:00", "16:00"),
                ("16:00", "18:00"),
            ],
        ),
        (
            "Переговорная Б",
            4,
            [
                ("10:00", "12:00"),
                ("13:00", "15:00"),
                ("15:00", "17:00"),
            ],
        ),
        (
            "Конференц-зал",
            20,
            [
                ("09:00", "12:00"),
                ("13:00", "16:00"),
                ("16:00", "19:00"),
            ],
        ),
    ]

    created_rooms = []
    for room_name, capacity, slots in rooms_data:
        try:
            room = room_repo.create(
                name=room_name,
                description=f"Комната для встреч, вместимость {capacity} человек",
                capacity=capacity,
                is_active=True,
            )
            created_rooms.append(room)
            print(f"     [+] Комната '{room_name}' создана (ID: {room.id})")

            created_slots = []
            for start, end in slots:
                time_slot = time_slot_repo.create(
                    room_id=room.id,
                    start_time=time.fromisoformat(start),
                    end_time=time.fromisoformat(end),
                    is_active=True,
                )
                created_slots.append(time_slot)

            room.time_slots = created_slots
            db.commit()

            print(f"        [+] Создано {len(created_slots)} временных слотов")

        except Exception as e:
            print(f"     [X] Ошибка при создании комнаты '{room_name}': {e}")
            db.rollback()
            continue

    if not created_rooms:
        raise Exception("Не удалось создать ни одной комнаты!")

    for i, room in enumerate(created_rooms):
        if not room.time_slots:
            raise Exception(
                f"У комнаты '{room.name}' (ID: {room.id}) нет временных слотов!"
            )

    print("  [ ] Создаем тестовые бронирования...")
    today = date.today()

    rooms_with_slots = [r for r in created_rooms if r.time_slots]

    if len(rooms_with_slots) < 3:
        raise Exception(
            f"Недостаточно комнат со слотами. Найдено: {len(rooms_with_slots)}, нужно: 3"
        )

    try:
        if rooms_with_slots[0].time_slots:
            booking1 = booking_repo.create(
                room_id=rooms_with_slots[0].id,
                time_slot_id=rooms_with_slots[0].time_slots[0].id,
                user_id=users[0].id,
                booking_date=today,
                description="Встреча с клиентом",
                status="active",
            )
            print(f"     [+] Бронирование #{booking1.id} (Алиса, {today})")
        else:
            print("     [X] У комнаты А нет слотов, пропускаем бронирование")

        if len(rooms_with_slots) > 1 and rooms_with_slots[1].time_slots:
            booking2 = booking_repo.create(
                room_id=rooms_with_slots[1].id,
                time_slot_id=rooms_with_slots[1].time_slots[0].id,
                user_id=users[0].id,
                booking_date=today,
                description="Планирование спринта",
                status="active",
            )
            print(f"     [+] Бронирование #{booking2.id} (Алиса, {today})")

        if len(rooms_with_slots[0].time_slots) > 1:
            booking3 = booking_repo.create(
                room_id=rooms_with_slots[0].id,
                time_slot_id=rooms_with_slots[0].time_slots[1].id,
                user_id=users[1].id,
                booking_date=today,
                description="Демо продукта",
                status="active",
            )
            print(f"     [+] Бронирование #{booking3.id} (Боб, {today})")

        if len(rooms_with_slots) > 2 and rooms_with_slots[2].time_slots:
            booking4 = booking_repo.create(
                room_id=rooms_with_slots[2].id,
                time_slot_id=rooms_with_slots[2].time_slots[0].id,
                user_id=users[2].id,
                booking_date=today,
                description="Отмененная встреча",
                status="active",
            )
            print(
                f"     [+] Бронирование #{booking4.id} (Чарли, {today}) - будет отменено"
            )

            booking_repo.cancel_booking(booking4.id, admin.id)
            print(f"     [X] Бронирование #{booking4.id} отменено администратором")

    except Exception as e:
        print(f"     [X] Ошибка при создании бронирований: {e}")
        db.rollback()
        raise

    print("[X] База данных успешно заполнена тестовыми данными!")


def main():
    """Основная функция для запуска скрипта"""
    print("=" * 50)
    print("  Заполнение БД тестовыми данными")
    print("=" * 50)

    db = SessionLocal()
    try:
        seed_database(db)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[X] Ошибка при заполнении БД: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

    print("=" * 50)
    print("  [+] Заполнение БД прошло успешно")
    print("=" * 50)


if __name__ == "__main__":
    main()
