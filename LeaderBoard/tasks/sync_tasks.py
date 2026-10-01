import logging
from celery import shared_task

from LeaderBoard.integrations import get_tpu_client, get_vitrina_client
from LeaderBoard.services import run_full_tpu_sync, run_full_vitrina_sync


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_tpu_students(self):
    """Синхронизация студентов из API ТПУ"""
    try:
        client = get_tpu_client()
        result = run_full_tpu_sync(client)
        logger.info(f"TPU sync task completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"TPU sync task failed: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def sync_vitrina_data(self):
    """Синхронизация проектов и активностей из Витрины"""
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
    """Полная синхронизация всех данных"""
    from celery import chain
    from LeaderBoard.tasks.rating_tasks import recalculate_ratings
    
    task_chain = chain(
        sync_tpu_students.s(),
        sync_vitrina_data.s(),
        recalculate_ratings.s(),
    )
    return task_chain.apply_async()