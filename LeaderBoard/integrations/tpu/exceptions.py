class TPUApiError(Exception):
    """Базовое исключение API ТПУ"""
    pass


class TPUApiAuthError(TPUApiError):
    """Ошибка авторизации в API ТПУ"""
    pass


class TPUApiNotFoundError(TPUApiError):
    """Запрашиваемый ресурс не найден"""
    pass


class TPUApiTimeoutError(TPUApiError):
    """Таймаут API ТПУ"""
    pass