from django.db.models import QuerySet, Q
from LeaderBoard.models import Students


def get_all_students() -> QuerySet[Students]:
    """Возвращает всех студентов с оптимизацией"""
    return Students.objects.select_related('user')


def get_student_by_login(login: str) -> Students:
    """Возвращает студента по логину с оптимизацией"""
    return Students.objects.select_related('user').get(login=login)


def get_students_with_activity() -> QuerySet[Students]:
    """Возвращает студентов, у которых есть часы работы"""
    return Students.objects.filter(history_work_all__gt=0).select_related('user')


def search_students_by_name(queryset: QuerySet[Students], search: str) -> QuerySet[Students]:
    """Ищет студентов по ФИО"""
    return queryset.filter(
        Q(first_name__icontains=search) |
        Q(last_name__icontains=search) |
        Q(patronymic__icontains=search)
    )