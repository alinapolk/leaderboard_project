from celery import shared_task
from django.utils import timezone
from .models import Students
from .services import calculate_rating_score


@shared_task
def recalculate_ratings():
    """
    Пересчитывает rating_score для ВСЕХ студентов.
    Запускается по расписанию через Celery Beat.
    """
    print(f'[{timezone.now()}] Начинаю пересчёт рейтинга...')

    students = Students.objects.all()
    total = students.count()
    updated = 0

    for student in students:
        new_rating = calculate_rating_score(
            student.study_score,
            student.history_work_all
        )
        current = float(student.rating_score or 0)

        if abs(current - new_rating) > 0.000001:
            student.rating_score = new_rating
            student.save(update_fields=['rating_score'])
            updated += 1

    result = f'Обновлено {updated} из {total} студентов'
    print(f'[{timezone.now()}] {result}')
    return result