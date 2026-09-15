from celery import shared_task
from django.utils import timezone
from LeaderBoard.services import recalculate_all_ratings


@shared_task
def recalculate_ratings():
    """
    Пересчитывает rating_score для ВСЕХ студентов.
    Запускается по расписанию через Celery Beat.
    
    Использует bulk_update для производительности.
    """
    print(f'[{timezone.now()}] Начинаю пересчёт рейтинга...')
    
    result = recalculate_all_ratings(reason='weekly_recalc', create_snapshots=False)
    
    print(f'[{timezone.now()}] {result["message"]}')
    return result['message']