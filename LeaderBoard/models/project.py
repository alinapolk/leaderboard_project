from django.db import models


class Projects(models.Model):
    """Таблица проектов"""
    id_project = models.AutoField(primary_key=True)
    external_id = models.CharField(max_length=50, unique=True, null=True)
    project_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    project_type = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=100, blank=True)
    partner = models.CharField(max_length=200, blank=True)
    is_promoted = models.BooleanField(default=False)
    info_akadem = models.TextField(blank=True, null=True) # Информация об академах/переводах для анализа отсева

    class Meta:
        db_table = 'projects'


class ProjectCheckpoint(models.Model):
    """Таблица для хранения дедлайнов"""
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='checkpoints')
    external_id = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=200)
    deadline = models.DateField()
    is_custom = models.BooleanField(default=False)

    class Meta:
        db_table = 'project_checkpoints'
        unique_together = ['project', 'title']