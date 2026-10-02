from django.db.models import QuerySet
from LeaderBoard.models import Student_Activity


def get_all_activity() -> QuerySet[Student_Activity]:
    """Возвращает все записи активности с оптимизацией"""
    return Student_Activity.objects.select_related('student', 'team__project')


def get_student_activity(student_login: str) -> QuerySet[Student_Activity]:
    """Возвращает активность студента с оптимизацией"""
    return Student_Activity.objects.select_related(
        'student', 'team__project'
    ).filter(student_id=student_login)