from django.db.models.signals import pre_save
from django.dispatch import receiver

from LeaderBoard.models import Students
from LeaderBoard.services import calculate_rating_score


@receiver(pre_save, sender=Students)
def update_rating_score(sender, instance, **kwargs):
    """
    Срабатывает перед каждым сохранением студента.
    Пересчитывает rating_score на основе текущих study_score и history_work_all.
    """
    instance.rating_score = calculate_rating_score(
        instance.study_score,
        instance.history_work_all
    )