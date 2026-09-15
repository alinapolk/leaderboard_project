def get_full_name(last_name: str, first_name: str, patronymic: str = None) -> str:
    """
    Формирует полное ФИО из отдельных частей.
    
    Пример:
    >>> get_full_name("Иванов", "Иван", "Иванович")
    "Иванов Иван Иванович"
    
    >>> get_full_name("Иванов", "Иван")
    "Иванов Иван"
    """
    parts = [last_name, first_name]
    if patronymic:
        parts.append(patronymic)
    return ' '.join(parts)


def get_client_ip(request) -> str:
    """
    Получает IP-адрес клиента из запроса.
    
    Учитывает заголовок X-Forwarded-For для работы за прокси.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip