from django.db.models import QuerySet
from LeaderBoard.models import Students, Projects


def get_leaderboard_students(search: str = None) -> QuerySet[Students]:
    """
    Возвращает студентов для лидерборда.
    
    Отсортировано по рейтингу, ограничено топ-50(хардкод).
    """
    from .students import get_students_with_activity, search_students_by_name
    
    queryset = get_students_with_activity()
    
    if search:
        queryset = search_students_by_name(queryset, search)
    
    queryset = queryset.order_by('-rating_score', '-study_score', '-history_work_all')
    return queryset[:50]


def get_leaderboard_projects() -> QuerySet[Projects]:
    """Возвращает проекты для лидерборда"""
    from .projects import get_all_projects
    return get_all_projects()