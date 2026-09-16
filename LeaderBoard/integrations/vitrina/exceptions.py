class VitrinaApiError(Exception):
    """Базовое исключение API Витрины"""
    pass


class VitrinaApiAuthError(VitrinaApiError):
    """Ошибка авторизации"""
    pass


class VitrinaApiNotFoundError(VitrinaApiError):
    """Ресурс не найден"""
    pass