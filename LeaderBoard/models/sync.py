from django.db import models


class ExternalSource(models.Model):
    """
    Источник данных (API ТПУ, API Витрины и т.д.).
    """
    code = models.CharField(max_length=50, unique=True, help_text="Код источника (например, TPU, VITRINA)")
    name = models.CharField(max_length=100, help_text="Название источника")
    base_url = models.URLField(blank=True, null=True, help_text="Базовый URL API")
    is_active = models.BooleanField(default=True, help_text="Источник активен")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'external_sources'
        verbose_name = 'Внешний источник'
        verbose_name_plural = 'Внешние источники'

    def __str__(self):
        return f"{self.name} ({self.code})"


class SyncRun(models.Model):
    """
    Запуск синхронизации данных из внешнего источника.
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('running', 'Выполняется'),
        ('success', 'Успешно'),
        ('failed', 'Ошибка'),
        ('partial_success', 'Частично успешно'),
    ]

    source = models.ForeignKey(
        ExternalSource,
        on_delete=models.CASCADE,
        related_name='sync_runs',
        verbose_name='Источник'
    )
    task_name = models.CharField(
        max_length=100,
        help_text="Название задачи (например, sync_tpu_students)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Начало')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='Окончание')
    records_received = models.IntegerField(default=0, verbose_name='Получено записей')
    records_created = models.IntegerField(default=0, verbose_name='Создано')
    records_updated = models.IntegerField(default=0, verbose_name='Обновлено')
    records_skipped = models.IntegerField(default=0, verbose_name='Пропущено')
    records_failed = models.IntegerField(default=0, verbose_name='Ошибок')
    error_message = models.TextField(blank=True, null=True, verbose_name='Сообщение об ошибке')

    class Meta:
        db_table = 'sync_runs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['source', '-started_at']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'Запуск синхронизации'
        verbose_name_plural = 'Запуски синхронизации'

    def __str__(self):
        return f"{self.source.code} — {self.task_name} [{self.status}] ({self.started_at})"

    @property
    def duration_seconds(self):
        """Длительность синхронизации в секундах"""
        if self.finished_at and self.started_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None


class SyncError(models.Model):
    """
    Ошибка по конкретной записи во время синхронизации.
    """
    sync_run = models.ForeignKey(
        SyncRun,
        on_delete=models.CASCADE,
        related_name='errors',
        verbose_name='Запуск синхронизации'
    )
    external_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Внешний ID записи (login, id_project и т.д.)"
    )
    payload = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Исходные данные',
        help_text="Данные, которые не удалось обработать"
    )
    error_message = models.TextField(verbose_name='Сообщение об ошибке')
    error_type = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sync_errors'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sync_run', '-created_at']),
        ]
        verbose_name = 'Ошибка синхронизации'
        verbose_name_plural = 'Ошибки синхронизации'

    def __str__(self):
        return f"Error for {self.external_id or 'unknown'}: {self.error_message[:100]}"


class RawApiLog(models.Model):
    """
    Сырой ответ от внешнего API.
    
    Полезен для диагностики: когда что-то пошло не так, можно посмотреть,
    что реально вернул внешний API.
    """
    source = models.ForeignKey(
        ExternalSource,
        on_delete=models.CASCADE,
        related_name='raw_logs',
        verbose_name='Источник'
    )
    sync_run = models.ForeignKey(
        SyncRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='raw_logs',
        verbose_name='Запуск синхронизации'
    )
    endpoint = models.CharField(max_length=255, verbose_name='Endpoint')
    request_params = models.JSONField(null=True, blank=True, verbose_name='Параметры запроса')
    request_body = models.JSONField(null=True, blank=True, verbose_name='Тело запроса')
    status_code = models.IntegerField(null=True, blank=True, verbose_name='HTTP статус')
    response_body = models.JSONField(null=True, blank=True, verbose_name='Тело ответа')
    error_message = models.TextField(blank=True, null=True, verbose_name='Ошибка')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'raw_api_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source', '-created_at']),
            models.Index(fields=['sync_run']),
        ]
        verbose_name = 'Сырой лог API'
        verbose_name_plural = 'Сырые логи API'

    def __str__(self):
        return f"{self.source.code} {self.endpoint} [{self.status_code or 'error'}]"