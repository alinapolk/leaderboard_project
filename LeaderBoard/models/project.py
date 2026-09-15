from django.db import models


class Projects(models.Model):
    """Таблица проектов"""
    id_project = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    info_akadem = models.TextField(blank=True, null=True) # Информация об академах/переводах для анализа отсева

    class Meta:
        db_table = 'projects'