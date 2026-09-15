from celery import shared_task


@shared_task
def sync_tpu_students():
    """
    Синхронизация студентов из API ТПУ.
    Будет реализовано в Этапе 4.
    """
    pass


@shared_task
def sync_vitrina_projects():
    """
    Синхронизация проектов из API Витрины.
    Будет реализовано в Этапе 4.
    """
    pass


@shared_task
def sync_all_data():
    """
    Полная синхронизация всех данных.
    Будет реализовано в Этапе 4.
    """
    pass