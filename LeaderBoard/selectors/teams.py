from django.db.models import QuerySet
from LeaderBoard.models import Teams, Student_Teams


def get_all_teams() -> QuerySet[Teams]:
    """Возвращает все команды"""
    return Teams.objects.all()


def get_team_by_id(team_id: int) -> Teams:
    """Возвращает команду по ID"""
    return Teams.objects.get(team_id=team_id)


def get_student_teams(student_login: str) -> QuerySet[Student_Teams]:
    """Возвращает команды студента"""
    return Student_Teams.objects.filter(student_id=student_login)