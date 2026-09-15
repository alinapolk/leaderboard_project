from django.db.models import QuerySet
from LeaderBoard.models import Student_Activity


def get_all_activity() -> QuerySet[Student_Activity]:
    """Возвращает все записи активности"""
    return Student_Activity.objects.all()


def get_student_activity(student_login: str) -> QuerySet[Student_Activity]:
    """Возвращает активность студента"""
    return Student_Activity.objects.filter(student_id=student_login)