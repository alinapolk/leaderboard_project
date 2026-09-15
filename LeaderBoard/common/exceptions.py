from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Единый обработчик ошибок для всего проекта.
    
    Формат ответа при ошибке:
    {
        "error": {
            "code": "validation_error",
            "message": "Описание ошибки",
            "details": {}
        }
    }
    """
    # Сначала вызываем стандартный обработчик DRF
    response = exception_handler(exc, context)

    if response is not None:
        # Определяем код ошибки на основе статуса
        error_code = _get_error_code(response.status_code)
        
        # Формируем единый формат ошибки
        custom_response_data = {
            'error': {
                'code': error_code,
                'message': _get_error_message(response.data),
                'details': response.data if isinstance(response.data, dict) else {}
            }
        }
        response.data = custom_response_data

    return response


def _get_error_code(status_code):
    """Определяет код ошибки по HTTP статусу"""
    codes = {
        400: 'validation_error',
        401: 'unauthorized',
        403: 'permission_denied',
        404: 'not_found',
        405: 'method_not_allowed',
        429: 'too_many_requests',
        500: 'internal_error',
    }
    return codes.get(status_code, 'unknown_error')


def _get_error_message(data):
    """Извлекает сообщение об ошибке из данных"""
    if isinstance(data, dict):
        # DRF обычно возвращает ошибки в формате {"field": ["error"]}
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                return str(value[0])
            elif isinstance(value, str):
                return value
        return "Произошла ошибка"
    elif isinstance(data, list) and len(data) > 0:
        return str(data[0])
    return "Произошла ошибка"


# Кастомные исключения проекта
class LeaderboardException(Exception):
    """Базовое исключение проекта"""
    def __init__(self, message="Произошла ошибка", code="leaderboard_error"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class StudentNotFoundException(LeaderboardException):
    """Студент не найден"""
    def __init__(self, message="Студент не найден"):
        super().__init__(message=message, code="student_not_found")


class ConsentRequiredException(LeaderboardException):
    """Требуется согласие на обработку данных"""
    def __init__(self, message="Необходимо дать согласие на обработку персональных данных"):
        super().__init__(message=message, code="consent_required")


class RatingCalculationError(LeaderboardException):
    """Ошибка при расчёте рейтинга"""
    def __init__(self, message="Ошибка при расчёте рейтинга"):
        super().__init__(message=message, code="rating_calculation_error")