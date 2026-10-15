from django.core.management.base import BaseCommand
from LeaderBoard.integrations.factory import get_vitrina_client
from LeaderBoard.services import run_full_vitrina_sync


class Command(BaseCommand):
    help = 'Запускает синхронизацию с Витриной (проекты + команды + студенты)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n🏛️ Синхронизация данных из Витрины...'))
        self.stdout.write(self.style.WARNING('   (студенты подтягиваются через role.places → TPU /users/{id})\n'))
        
        try:
            client = get_vitrina_client()
            result = run_full_vitrina_sync(client)
            
            self.stdout.write(self.style.SUCCESS('\n✅ Синхронизация завершена:'))
            for key, value in result.items():
                if value:
                    self.stdout.write(f'  {key}: {value}')
            
            self.stdout.write(self.style.SUCCESS('\n🎉 Все данные обновлены!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Ошибка синхронизации: {e}'))
            raise