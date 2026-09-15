from django.db import models
from .project import Projects


class Teams(models.Model):
    """Таблица команд"""
    team_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(                    # Связь с проектом
        Projects,
        on_delete=models.CASCADE,
        db_column='project_id'
    )
    expert_score = models.CharField(max_length=10, blank=True, null=True)
    period_start = models.DateField(blank=True, null=True)
    period_end = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'teams'