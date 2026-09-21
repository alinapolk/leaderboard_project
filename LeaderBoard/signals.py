from django.db.models.signals import pre_save
from django.dispatch import receiver

from LeaderBoard.models import Students
from LeaderBoard.services.rating_service import calculate_all_periods_rating, PERIOD_RATING_FIELD


@receiver(pre_save, sender=Students)
def update_rating_score(sender, instance, **kwargs):
    """
    Срабатывает перед каждым сохранением студента.
    Пересчитывает рейтинги за все периоды.
    """
    ratings = calculate_all_periods_rating(instance)
    
    for period, rating in ratings.items():
        field = PERIOD_RATING_FIELD[period]
        setattr(instance, field, rating)