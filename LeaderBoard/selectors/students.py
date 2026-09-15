from django.db.models import QuerySet
from LeaderBoard.models import Students


def get_all_students() -> QuerySet[Students]:
    """Возвращает всех студентов"""
    return Students.objects.all()


def get_student_by_login(login: str) -> Students:
    """Возвращает студента по логину"""
    return Students.objects.get(login=login)


def get_students_with_activity() -> QuerySet[Students]:
    """Возвращает студентов, у которых есть часы работы"""
    return Students.objects.filter(history_work_all__gt=0)


def search_students_by_name(queryset: QuerySet[Students], search: str) -> QuerySet[Students]:
    """Ищет студентов по ФИО"""
    from django.db.models import Q
    return queryset.filter(
        Q(first_name__icontains=search) |
        Q(last_name__icontains=search) |
        Q(patronymic__icontains=search)
    )