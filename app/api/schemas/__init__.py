from .common import (
    BaseResponse,
    PaginationParams,
    PaginatedResponse,
    ErrorResponse,
)
from .auth import (
    LoginRequest,
    TokenResponse,
)
from .user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserSelfUpdate,
)
from .room import (
    RoomCreate,
    RoomUpdate,
    RoomResponse,
    RoomAvailabilityResponse,
)
from .timeslot import (
    TimeSlotCreate,
    TimeSlotUpdate,
    TimeSlotResponse,
)
from .booking import (
    BookingCreate,
    BookingUpdate,
    BookingCancel,
    BookingResponse,
    BookingHistoryResponse,
)

__all__ = [
    "BaseResponse",
    "PaginationParams",
    "PaginatedResponse",
    "ErrorResponse",
    "LoginRequest",
    "TokenResponse",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "UserSelfUpdate",
    "RoomCreate",
    "RoomUpdate",
    "RoomResponse",
    "RoomAvailabilityResponse",
    "TimeSlotCreate",
    "TimeSlotUpdate",
    "TimeSlotResponse",
    "BookingCreate",
    "BookingUpdate",
    "BookingCancel",
    "BookingResponse",
    "BookingHistoryResponse",
]
