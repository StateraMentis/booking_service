from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from app.core.database import engine
from app.core.config import settings
from app.api.routers import (
    auth_router,
    users_router,
    rooms_router,
    time_slots_router,
    bookings_router,
)
from app.exceptions import DomainError
from app.api.exceptions import (
    domain_error_handler,
    validation_error_handler,
    integrity_error_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    Выполняется при старте и остановке
    """

    yield

    engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(rooms_router, prefix="/api/v1")
app.include_router(time_slots_router, prefix="/api/v1")
app.include_router(bookings_router, prefix="/api/v1")

app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)


@app.get("/")
async def root():
    return {
        "message": "Meeting Room Booking Service",
        "docs": "/api/docs",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
