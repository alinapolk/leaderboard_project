from django.core.management.base import BaseCommand
from LeaderBoard.integrations.factory import get_vitrina_client
from LeaderBoard.services import run_full_vitrina_sync


class Command(BaseCommand):
    help = 'Запускает полную синхронизацию с Витриной'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Запуск синхронизации Витрины...')
        
        client = get_vitrina_client()
        result = run_full_vitrina_sync(client)
        
        self.stdout.write(self.style.SUCCESS('\n✅ Синхронизация завершена:'))
        for key, value in result.items():
            self.stdout.write(f'  {key}: {value}')