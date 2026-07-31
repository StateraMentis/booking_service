from datetime import time
from unittest.mock import MagicMock

import pytest
from app.api.schemas.timeslot import TimeSlotCreate
from app.exceptions import (
    RoomNotFoundError,
    TimeSlotNotFoundError,
    TimeSlotOverlapError,
)
from app.services.timeslot_service import TimeSlotService


def test_get_room_slots_raises_if_room_missing():
    room_repo = MagicMock(get_by_id=MagicMock(return_value=None))
    service = TimeSlotService(
        db=None,
        time_slot_repo=MagicMock(),
        room_repo=room_repo,
        booking_repo=MagicMock(),
    )

    with pytest.raises(RoomNotFoundError):
        service.get_room_slots(1)


def test_create_time_slot_raises_if_room_missing():
    room_repo = MagicMock(get_by_id=MagicMock(return_value=None))
    service = TimeSlotService(
        db=None,
        time_slot_repo=MagicMock(),
        room_repo=room_repo,
        booking_repo=MagicMock(),
    )
    payload = TimeSlotCreate(room_id=1, start_time=time(9, 0), end_time=time(10, 0))

    with pytest.raises(RoomNotFoundError):
        service.create_time_slot(payload)


def test_create_time_slot_raises_on_overlap():
    room_repo = MagicMock(get_by_id=MagicMock(return_value=object()))
    time_slot_repo = MagicMock()
    time_slot_repo.ensure_no_overlap.side_effect = TimeSlotOverlapError("Overlap")
    service = TimeSlotService(
        db=None,
        time_slot_repo=time_slot_repo,
        room_repo=room_repo,
        booking_repo=MagicMock(),
    )
    payload = TimeSlotCreate(room_id=1, start_time=time(9, 0), end_time=time(10, 0))

    with pytest.raises(TimeSlotOverlapError):
        service.create_time_slot(payload)


def test_update_time_slot_raises_if_not_found():
    time_slot_repo = MagicMock(get_by_id=MagicMock(return_value=None))
    service = TimeSlotService(
        db=None,
        time_slot_repo=time_slot_repo,
        room_repo=MagicMock(),
        booking_repo=MagicMock(),
    )

    with pytest.raises(TimeSlotNotFoundError):
        service.update_time_slot(1, {"start_time": time(10, 0)})


def test_update_time_slot_checks_overlap():
    slot = MagicMock(
        room_id=1, start_time=time(9, 0), end_time=time(10, 0), day_of_week=None
    )
    time_slot_repo = MagicMock(
        get_by_id=MagicMock(return_value=slot), ensure_no_overlap=MagicMock()
    )
    service = TimeSlotService(
        db=None,
        time_slot_repo=time_slot_repo,
        room_repo=MagicMock(),
        booking_repo=MagicMock(),
    )

    service.update_time_slot(1, {"start_time": time(9, 30), "end_time": time(10, 30)})

    time_slot_repo.ensure_no_overlap.assert_called_once()


def test_delete_time_slot_returns_false_when_not_found():
    time_slot_repo = MagicMock(
        get_by_id=MagicMock(return_value=None), delete=MagicMock(return_value=False)
    )
    service = TimeSlotService(
        db=None,
        time_slot_repo=time_slot_repo,
        room_repo=MagicMock(),
        booking_repo=MagicMock(),
    )

    assert service.delete_time_slot(123) is False
