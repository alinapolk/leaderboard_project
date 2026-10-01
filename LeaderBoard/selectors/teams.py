from django.db.models import QuerySet
from LeaderBoard.models import Teams, Student_Teams


def get_all_teams() -> QuerySet[Teams]:
    """Возвращает все команды с оптимизацией"""
    return Teams.objects.select_related('project').prefetch_related('student_teams_set')


def get_team_by_id(team_id: int) -> Teams:
    """Возвращает команду по ID с оптимизацией"""
    return Teams.objects.select_related('project').prefetch_related(
        'student_teams_set__student'
    ).get(team_id=team_id)


def get_student_teams(student_login: str) -> QuerySet[Student_Teams]:
    """Возвращает команды студента с оптимизацией"""
    return Student_Teams.objects.select_related(
        'team__project', 'student'
    ).filter(student_id=student_login)