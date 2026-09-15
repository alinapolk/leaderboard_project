from django.db import models
from .student import Students


class RatingSnapshot(models.Model):
    """
    История изменений рейтинга студента.
    
    Каждый пересчёт рейтинга создаёт новый снимок.
    """
    REASON_CHOICES = [
        ('manual_recalc', 'Ручной пересчёт'),
        ('weekly_recalc', 'Еженедельный пересчёт'),
        ('after_sync', 'После синхронизации'),
        ('formula_change', 'Изменение формулы'),
        ('admin_action', 'Действие администратора'),
    ]

    student = models.ForeignKey(
        Students,
        on_delete=models.CASCADE,
        related_name='rating_snapshots',
        db_column='student_login'
    )
    
    score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Итоговый рейтинговый балл"
    )
    
    study_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Оценка успеваемости на момент расчёта"
    )
    
    history_work_all = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Суммарные часы на момент расчёта"
    )
    
    study_component = models.DecimalField(
        max_digits=8,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Компонента успеваемости в рейтинге"
    )
    
    work_component = models.DecimalField(
        max_digits=8,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Компонента часов в рейтинге"
    )
    
    formula_version = models.CharField(
        max_length=20,
        default='v1',
        help_text="Версия формулы расчёта"
    )
    
    reason = models.CharField(
        max_length=30,
        choices=REASON_CHOICES,
        default='manual_recalc',
        help_text="Причина пересчёта"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rating_snapshots'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', '-created_at']),
        ]

    def __str__(self):
        return f"{self.student.login}: {self.score} ({self.created_at})"