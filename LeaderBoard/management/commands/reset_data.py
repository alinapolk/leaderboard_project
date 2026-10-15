from django.core.management.base import BaseCommand
from django.db import transaction

from LeaderBoard.models import (
    Students, Projects, Teams, Student_Teams, 
    Student_Activity, ProjectCheckpoint,
    SyncRun, SyncError, RawApiLog
)


class Command(BaseCommand):
    help = 'Очищает все бизнес-данные (студенты, проекты, команды), оставляя пользователей и админку'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep-sync-logs',
            action='store_true',
            help='Не очищать историю синхронизаций (SyncRun, SyncError, RawApiLog)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n🧹 Начинаем очистку базы данных...\n'))
        
        # Порядок важен из-за foreign key связей
        tables_to_clean = [
            ('Student_Teams', Student_Teams),
            ('Student_Activity', Student_Activity),
            ('ProjectCheckpoint', ProjectCheckpoint),
            ('Teams', Teams),
            ('Projects', Projects),
            ('Students', Students),
        ]
        
        # Опционально — логи синхронизаций
        if not options['keep_sync_logs']:
            tables_to_clean.extend([
                ('RawApiLog', RawApiLog),
                ('SyncError', SyncError),
                ('SyncRun', SyncRun),
            ])
        
        total_deleted = 0
        for name, model in tables_to_clean:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ {name}: удалено {count} записей')
                )
                total_deleted += count
            else:
                self.stdout.write(f'  · {name}: пусто')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Очищено всего записей: {total_deleted}')
        )
        self.stdout.write(self.style.SUCCESS(
            '💡 Пользователи, ExternalSource и админка сохранены\n'
        ))