from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Стандартная пагинация с номерами страниц.
    
    Использование:
    ?page=1&page_size=50
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class LeaderboardPagination(LimitOffsetPagination):
    """
    Пагинация для лидерборда с limit/offset.
    
    Использование:
    ?limit=50&offset=0
    """
    default_limit = 50
    max_limit = 100