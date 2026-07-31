from .auth import router as auth_router
from .users import router as users_router
from .rooms import router as rooms_router
from .timeslots import router as time_slots_router
from .bookings import router as bookings_router

__all__ = [
    "auth_router",
    "users_router",
    "rooms_router",
    "time_slots_router",
    "bookings_router",
]
