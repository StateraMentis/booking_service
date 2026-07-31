from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from app.exceptions import DomainError


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    """
    Универсальный обработчик для всех доменных ошибок
    """

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "status_code": exc.status_code,
        },
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Обработчик ошибок Pydantic (422)
    """

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "detail": "Ошибка валидации",
            "errors": exc.errors(),
        },
    )


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """
    Обработчик ошибок БД
    """

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": "Конфликт данных. Возможно, такая запись уже существует.",
        },
    )
