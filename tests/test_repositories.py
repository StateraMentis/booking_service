from datetime import date, time

import pytest
from app.enums import BookingStatus, UserRole
from app.models.room import MeetingRoomORM
from app.models.timeslot import TimeSlotORM
from app.models.user import UserORM
from app.repositories.booking_repository import BookingRepository
from app.repositories.timeslot_repository import TimeSlotRepository
from app.repositories.user_repository import UserRepository


def test_user_repository_create_and_lookup(db):
    user_repo = UserRepository(db)
    user = user_repo.create_user(
        username="JohnDoe",
        email="John@Example.com",
        password="StrongPass123",
        full_name="John Doe",
        role=UserRole.EMPLOYEE,
    )

    assert user.id is not None
    assert user.username == "johndoe"
    assert user.email == "john@example.com"
    assert user.password_hash != "StrongPass123"
    assert user_repo.get_by_username("johndoe").id == user.id
    assert user_repo.get_by_username_or_email("john@example.com").id == user.id


def test_booking_repository_check_slot_availability_and_cancel(db):
    room = MeetingRoomORM(name="Room 1", description="Test room", capacity=4)
    db.add(room)
    db.flush()

    timeslot = TimeSlotORM(
        room_id=room.id,
        start_time=time(10, 0),
        end_time=time(11, 0),
    )
    db.add(timeslot)
    db.flush()

    user = UserORM(
        username="jane",
        email="jane@example.com",
        password_hash="hashvalue",
        role=UserRole.EMPLOYEE,
        is_active=True,
    )
    db.add(user)
    db.flush()

    booking_repo = BookingRepository(db)
    active_booking = booking_repo.create(
        room_id=room.id,
        time_slot_id=timeslot.id,
        user_id=user.id,
        booking_date=date.today(),
        description="Team sync",
        status=BookingStatus.ACTIVE.value,
    )

    assert not booking_repo.check_slot_availability(
        room_id=room.id,
        time_slot_id=timeslot.id,
        date=date.today(),
    )
    assert booking_repo.check_slot_availability(
        room_id=room.id,
        time_slot_id=timeslot.id,
        date=date.today(),
        exclude_id=active_booking.id,
    )

    cancelled = booking_repo.cancel_booking(active_booking.id, cancelled_by_id=user.id)
    assert cancelled is not None
    assert cancelled.status == BookingStatus.CANCELLED.value
    assert cancelled.cancelled_by_id == user.id


def test_timeslot_repository_raises_overlap_error(db):
    room = MeetingRoomORM(name="Room 2", description="Duplicate slot room", capacity=2)
    db.add(room)
    db.flush()

    existing_slot = TimeSlotORM(
        room_id=room.id,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )
    db.add(existing_slot)
    db.flush()

    timeslot_repo = TimeSlotRepository(db)

    with pytest.raises(Exception):
        timeslot_repo.ensure_no_overlap(
            room_id=room.id,
            start_time=time(9, 30),
            end_time=time(10, 30),
        )
