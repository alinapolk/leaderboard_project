from django.db.models import QuerySet
from LeaderBoard.models import Students, Projects
from LeaderBoard.services.rating_service import PERIOD_RATING_FIELD


def get_leaderboard_students(search: str = None, period: str = 'all') -> QuerySet[Students]:
    """
    Возвращает студентов для лидерборда.
    
    Отсортировано по рейтингу за указанный период, ограничено топ-50.
    """
    from .students import get_students_with_activity, search_students_by_name

    queryset = get_students_with_activity()

    if search:
        queryset = search_students_by_name(queryset, search)

    # Определяем поле для сортировки в зависимости от периода
    rating_field = PERIOD_RATING_FIELD.get(period, 'rating_score')
    
    queryset = queryset.order_by(
        f'-{rating_field}',
        '-study_score',
        '-history_work_all'
    )
    return queryset[:50]


def get_leaderboard_projects() -> QuerySet[Projects]:
    """Возвращает проекты для лидерборда"""
    from .projects import get_all_projects
    return get_all_projects()