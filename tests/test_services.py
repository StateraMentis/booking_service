from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
from app.api.schemas.booking import BookingCreate
from app.api.schemas.user import UserCreate
from app.enums import BookingStatus, UserRole
from app.exceptions import (
    BookingPermissionError,
    BookingAlreadyCancelledError,
    UserAlreadyExistsError,
    ValidationError,
    UserInactiveError,
)
from app.services.auth_service import AuthService
from app.services.booking_service import BookingService
from app.services.user_service import UserService


def test_user_service_create_user_raises_if_username_exists():
    repo = MagicMock()
    repo.get_by_username.return_value = object()
    repo.get_by_email.return_value = None

    service = UserService(db=None, user_repo=repo)

    with pytest.raises(UserAlreadyExistsError):
        service.create_user(
            UserCreate(
                username="john",
                email="john@example.com",
                password="StrongPass123",
                full_name="John Doe",
                role=UserRole.EMPLOYEE,
            )
        )


def test_user_service_update_user_role_requires_admin():
    repo = MagicMock()
    repo.get_by_id.return_value = object()
    repo.get_by_username.return_value = None
    repo.get_by_email.return_value = None

    service = UserService(db=None, user_repo=repo)

    with pytest.raises(ValidationError):
        service.update_user(1, {"role": UserRole.ADMIN}, is_admin=False)


from app.core.security import get_password_hash


def test_auth_service_authenticate_user_rejects_inactive_user():
    user = MagicMock()
    user.password_hash = get_password_hash("password")
    user.is_active = False
    repo = MagicMock()
    repo.get_by_username_or_email.return_value = user

    service = AuthService(db=None, user_repo=repo)

    with pytest.raises(UserInactiveError):
        service.authenticate_user("john", "password")


def test_booking_service_create_booking_happy_path():
    room_repo = MagicMock()
    timeslot_repo = MagicMock()
    booking_repo = MagicMock()
    user_repo = MagicMock()

    room_repo.get_by_id.return_value = object()
    timeslot_obj = MagicMock()
    timeslot_obj.room_id = 1
    timeslot_repo.get_by_id.return_value = timeslot_obj
    booking_repo.check_slot_availability.return_value = True
    booking_repo.create.return_value = object()

    service = BookingService(
        db=None,
        booking_repo=booking_repo,
        room_repo=room_repo,
        time_slot_repo=timeslot_repo,
        user_repo=user_repo,
    )

    booking_data = BookingCreate(
        room_id=1,
        time_slot_id=1,
        booking_date=date.today() + timedelta(days=1),
        description="Testing",
    )

    result = service.create_booking(booking_data, user_id=42)

    assert result is not None
    booking_repo.create.assert_called_once()


def test_booking_service_update_booking_blocks_cancelled():
    booking = MagicMock()
    booking.user_id = 5
    booking.status = BookingStatus.CANCELLED.value
    booking.room_id = 1
    booking.time_slot_id = 1
    booking.booking_date = date.today()

    booking_repo = MagicMock()
    booking_repo.get_by_id.return_value = booking

    service = BookingService(
        db=None,
        booking_repo=booking_repo,
        room_repo=MagicMock(),
        time_slot_repo=MagicMock(),
        user_repo=MagicMock(),
    )

    with pytest.raises(BookingAlreadyCancelledError):
        service.update_booking(1, {"description": "new"}, user_id=5)


def test_booking_service_cancel_booking_requires_permission():
    booking = MagicMock()
    booking.user_id = 10
    booking.status = BookingStatus.ACTIVE.value

    booking_repo = MagicMock()
    booking_repo.get_by_id.return_value = booking
    booking_repo.cancel_booking.return_value = booking

    service = BookingService(
        db=None,
        booking_repo=booking_repo,
        room_repo=MagicMock(),
        time_slot_repo=MagicMock(),
        user_repo=MagicMock(),
    )

    with pytest.raises(BookingPermissionError):
        service.cancel_booking(1, user_id=20)
