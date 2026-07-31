from datetime import date, timedelta

import pytest
from app.api.schemas.booking import BookingCreate, BookingUpdate
from app.api.schemas.user import UserCreate
from app.exceptions import BookingDateInPastError


def test_booking_create_rejects_past_date():
    yesterday = date.today() - timedelta(days=1)

    with pytest.raises(BookingDateInPastError):
        BookingCreate(room_id=1, time_slot_id=1, booking_date=yesterday)


def test_booking_update_rejects_past_date():
    yesterday = date.today() - timedelta(days=1)

    with pytest.raises(BookingDateInPastError):
        BookingUpdate(booking_date=yesterday)


def test_user_create_password_complexity_validation():
    with pytest.raises(ValueError):
        UserCreate(
            username="john_doe",
            email="john@example.com",
            password="simple",
            full_name="John Doe",
            role="employee",
        )
