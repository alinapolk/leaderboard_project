import logging
from celery import shared_task

from LeaderBoard.integrations import get_tpu_client, get_vitrina_client
from LeaderBoard.services import run_full_tpu_sync, run_full_vitrina_sync


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_tpu_students(self):
    """
    Синхронизация студентов из API ТПУ.
    
    При ошибке пытается повторить до 3 раз с экспоненциальной задержкой.
    """
    try:
        client = get_tpu_client()
        result = run_full_tpu_sync(client)
        logger.info(f"TPU sync task completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"TPU sync task failed: {exc}")
        # Повтор с экспоненциальной задержкой
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def sync_vitrina_projects(self):
    """Синхронизация проектов из API Витрины"""
    try:
        client = get_vitrina_client()
        result = run_full_vitrina_sync(client)
        logger.info(f"Vitrina sync task completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Vitrina sync task failed: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def sync_all_data():
    """Полная синхронизация всех данных — запускает цепочку задач"""
    from celery import chain
    from LeaderBoard.tasks.rating_tasks import recalculate_ratings
    
    # Цепочка: TPU -> Vitrina -> Пересчёт рейтинга
    task_chain = chain(
        sync_tpu_students.s(),
        sync_vitrina_projects.s(),
        recalculate_ratings.s(),
    )
    return task_chain.apply_async()