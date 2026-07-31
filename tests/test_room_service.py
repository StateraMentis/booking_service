from datetime import date
from unittest.mock import MagicMock

import pytest
from app.api.schemas.room import RoomCreate
from app.exceptions import (
    RoomAlreadyExistsError,
    RoomNotFoundError,
    RoomHasActiveBookingsError,
)
from app.models.room import MeetingRoomORM
from app.models.timeslot import TimeSlotORM
from app.services.room_service import RoomService


def test_create_room_raises_if_name_exists():
    repo = MagicMock()
    repo.get_by_name.return_value = object()
    service = RoomService(
        db=None, room_repo=repo, time_slot_repo=MagicMock(), booking_repo=MagicMock()
    )

    with pytest.raises(RoomAlreadyExistsError):
        service.create_room(RoomCreate(name="Room A", capacity=4))


def test_update_room_raises_if_not_found():
    repo = MagicMock()
    repo.get_by_id.return_value = None
    service = RoomService(
        db=None, room_repo=repo, time_slot_repo=MagicMock(), booking_repo=MagicMock()
    )

    with pytest.raises(RoomNotFoundError):
        service.update_room(1, {"name": "New name"})


def test_update_room_raises_if_name_conflict():
    room = MagicMock(id=1)
    conflicting_room = MagicMock(id=2)
    repo = MagicMock()
    repo.get_by_id.return_value = room
    repo.get_by_name.return_value = conflicting_room
    service = RoomService(
        db=None, room_repo=repo, time_slot_repo=MagicMock(), booking_repo=MagicMock()
    )

    with pytest.raises(RoomAlreadyExistsError):
        service.update_room(1, {"name": "Existing room"})


def test_delete_room_raises_when_active_bookings_exist():
    room = MagicMock(id=1)
    room_repo = MagicMock(get_by_id=MagicMock(return_value=room))
    booking_repo = MagicMock(get_room_bookings=MagicMock(return_value=[object()]))
    service = RoomService(
        db=None,
        room_repo=room_repo,
        time_slot_repo=MagicMock(),
        booking_repo=booking_repo,
    )

    with pytest.raises(RoomHasActiveBookingsError):
        service.delete_room(1)


def test_check_availability_returns_slots():
    room = MeetingRoomORM(name="Room A", description="Room A", capacity=4)
    room.id = 1
    room.name = "Room A"
    room.capacity = 4

    slot1 = TimeSlotORM(room_id=1, start_time="09:00", end_time="10:00", is_active=True)
    slot1.id = 1
    slot2 = TimeSlotORM(room_id=1, start_time="10:00", end_time="11:00", is_active=True)
    slot2.id = 2

    room_repo = MagicMock(get_by_id=MagicMock(return_value=room))
    time_slot_repo = MagicMock(
        get_active_slots_by_room=MagicMock(return_value=[slot1, slot2])
    )
    booking = MagicMock(time_slot_id=1)
    booking_repo = MagicMock(get_room_bookings=MagicMock(return_value=[booking]))

    service = RoomService(
        db=None,
        room_repo=room_repo,
        time_slot_repo=time_slot_repo,
        booking_repo=booking_repo,
    )

    availability = service.check_availability(1, date.today())

    assert availability["room_id"] == 1
    assert availability["booked_slots"] == 1
    assert availability["total_slots"] == 2
    assert availability["is_fully_booked"] is False
    assert len(availability["available_slots"]) == 1


def test_check_availability_returns_none_when_room_missing():
    room_repo = MagicMock(get_by_id=MagicMock(return_value=None))
    service = RoomService(
        db=None,
        room_repo=room_repo,
        time_slot_repo=MagicMock(),
        booking_repo=MagicMock(),
    )

    assert service.check_availability(999, date.today()) is None
