class DomainError(Exception):
    """
    Базовое исключение для доменных ошибок
    """

    status_code: int = 400

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        super().__init__(message)


class NotFoundError(DomainError):
    """
    Объект не найден
    """

    status_code = 404


class ConflictError(DomainError):
    """
    Конфликт данных
    """

    status_code = 409


class PermissionDeniedError(DomainError):
    """
    Недостаточно прав
    """

    status_code = 403


class ValidationError(DomainError):
    """
    Ошибка валидации
    """

    status_code = 400


class AuthenticationError(DomainError):
    """
    Ошибка аутентификации
    """

    status_code = 401


class UserNotFoundError(NotFoundError):
    """
    Пользователь не найден
    """

    pass


class UserAlreadyExistsError(ConflictError):
    """
    Пользователь уже существует
    """

    pass


class InvalidCredentialsError(AuthenticationError):
    """
    Неверные учетные данные
    """

    pass


class UserInactiveError(PermissionDeniedError):
    """
    Пользователь неактивен
    """

    pass


class RoomNotFoundError(NotFoundError):
    """
    Комната не найдена
    """

    pass


class RoomAlreadyExistsError(ConflictError):
    """
    Комната уже существует
    """

    pass


class RoomHasActiveBookingsError(ConflictError):
    """
    Комната имеет активные бронирования
    """

    pass


class TimeSlotNotFoundError(NotFoundError):
    """
    Временной слот не найден
    """

    pass


class TimeSlotOverlapError(ConflictError):
    """
    Слот пересекается с существующим
    """

    pass


class TimeSlotIncorrect(ValidationError):
    """
    Слот неправильно заполнен
    """

    pass


class BookingNotFoundError(NotFoundError):
    """
    Бронирование не найдено
    """

    pass


class BookingAlreadyCancelledError(ConflictError):
    """
    Бронирование уже отменено
    """

    pass


class SlotAlreadyBookedError(ConflictError):
    """
    Слот уже забронирован
    """

    pass


class BookingPermissionError(PermissionDeniedError):
    """
    Нет прав на это бронирование
    """

    pass


class BookingDateInPastError(ValidationError):
    """
    Дата бронирования в прошлом
    """

    pass
