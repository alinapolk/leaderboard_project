from django.db import models
from django.contrib.auth.models import User


class Students(models.Model):
    """Таблица студентов"""
    login = models.CharField(primary_key=True, max_length=50)
    someone_id = models.CharField(max_length=50, unique=True) # ID из API вуза для интеграции
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100, blank=True, null=True)
    student_group = models.CharField(max_length=20)
    direction_name = models.CharField(max_length=100)
    study_year = models.IntegerField(blank=True, null=True)
    faculty = models.CharField(max_length=100)
    study_score = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    debt_count = models.IntegerField(blank=True, null=True)
    top_view = models.CharField(max_length=100, blank=True, null=True) # Для категоризации студентов (лидер, активный, новичок и т.д.)
    
    history_work_sem = models.DecimalField(max_digits=8, decimal_places=2, default=0) # Часы за семестр для быстрого рейтинга
    history_work_week = models.DecimalField(max_digits=6, decimal_places=2, default=0) # Часы за неделю для быстрого рейтинга
    history_work_all = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Всего часов за всё время
    history_work_month = models.DecimalField(max_digits=8, decimal_places=2, default=0) # Часы за месяц для быстрого рейтинга
        
    # Рейтинги студентов за разные периоды
    rating_score = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, db_index=True, help_text="Рейтинг за всё время"
    )
    rating_score_week = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, db_index=True, help_text="Рейтинг за неделю"
    )
    rating_score_month = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, db_index=True, help_text="Рейтинг за месяц"
    )
    rating_score_sem = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, db_index=True, help_text="Рейтинг за семестр"
    )
    

    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='student_profil'
    )

    class Meta:
        db_table = 'students'

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.login})"
    
    def get_hours_for_period(self, period: str):
        """Возвращает часы за указанный период"""
        mapping = {
            'week': self.history_work_week,
            'month': self.history_work_month,
            'sem': self.history_work_sem,
            'all': self.history_work_all,
        }
        return mapping.get(period, self.history_work_all)
    
    def get_rating_for_period(self, period: str):
        """Возвращает рейтинг за указаннвый период"""
        mapping = {
            'week': self.rating_score_week,
            'month': self.rating_score_month,
            'sem': self.rating_score_sem,
            'all': self.rating_score,
        }
        return mapping.get(period, self.rating_score)
