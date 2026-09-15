from django.db.models import QuerySet
from LeaderBoard.models import Projects


def get_all_projects() -> QuerySet[Projects]:
    """Возвращает все проекты"""
    return Projects.objects.all()


def get_project_by_id(project_id: int) -> Projects:
    """Возвращает проект по ID"""
    return Projects.objects.get(id_project=project_id)