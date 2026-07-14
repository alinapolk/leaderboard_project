from django.core.management.base import BaseCommand
from LeaderBoard.models import Students
import random


class Command(BaseCommand):
    help = 'Заполняет базу 300 тестовыми студентами ИШИТР'

    def handle(self, *args, **kwargs):
        # Группы ИШИТР
        groups = ['8ВМ01', '8ВМ02', '8ВМ11', '8ВМ12', '8ВМ03', '8ВМ04']

        # Направления
        directions = [
            'Программная инженерия',
            'Информационные системы',
            'Прикладная информатика',
            'Робототехника',
            'Искусственный интеллект',
        ]

        # Фамилии
        surnames = [
            'Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов',
            'Попов', 'Васильев', 'Михайлов', 'Новиков', 'Фёдоров',
            'Морозов', 'Волков', 'Алексеев', 'Лебедев', 'Семёнов',
            'Егоров', 'Павлов', 'Козлов', 'Степанов', 'Николаев',
            'Орлов', 'Андреев', 'Макаров', 'Никитин', 'Захаров',
        ]

        # Имена
        names_male = [
            'Александр', 'Дмитрий', 'Максим', 'Сергей', 'Андрей',
            'Алексей', 'Илья', 'Кирилл', 'Никита', 'Иван',
            'Артём', 'Егор', 'Даниил', 'Владислав', 'Роман',
        ]

        names_female = [
            'Анастасия', 'Анна', 'Мария', 'Екатерина', 'Дарья',
            'Софья', 'Виктория', 'Полина', 'Александра', 'Елизавета',
            'Ксения', 'Валерия', 'Алёна', 'Юлия', 'Ольга',
        ]

        # Отчества
        patronymics_male = [
            'Александрович', 'Дмитриевич', 'Сергеевич', 'Андреевич',
            'Алексеевич', 'Иванович', 'Максимович', 'Артёмович',
        ]
        patronymics_female = [
            'Александровна', 'Дмитриевна', 'Сергеевна', 'Андреевна',
            'Алексеевна', 'Ивановна', 'Максимовна', 'Артёмовна',
        ]

        statuses = ['лидер', 'активный', 'новичок']

        # Удаляем старые данные (если нужно)
        # Students.objects.all().delete()

        self.stdout.write('Создаю 300 студентов...')

        for i in range(300):
            is_male = random.choice([True, False])
            surname = random.choice(surnames)

            if is_male:
                name = random.choice(names_male)
                patronymic = random.choice(patronymics_male)
            else:
                name = random.choice(names_female)
                patronymic = random.choice(patronymics_female)

            login = f'stu{str(i + 1).zfill(4)}'

            # Генерируем часы (от 0 до 500)
            hours_all = round(random.uniform(50, 500), 2)

            # Успеваемость (нормированная, макс 1.0)
            study_score = round(random.uniform(0.3, 1.0), 2)

            # Статус на основе часов
            if hours_all > 300:
                top_view = 'лидер'
            elif hours_all > 150:
                top_view = 'активный'
            else:
                top_view = 'новичок'

            student, created = Students.objects.update_or_create(
                login=login,
                defaults={
                    'someone_id': f'tpu-stu{str(i + 1).zfill(4)}',
                    'first_name': name,
                    'last_name': surname,
                    'patronymic': patronymic,
                    'student_group': random.choice(groups),
                    'direction_name': random.choice(directions),
                    'study_year': random.randint(1, 4),
                    'faculty': 'ИШИТР',
                    'study_score': study_score,
                    'debt_count': random.randint(0, 3),
                    'history_work_all': hours_all,
                    'history_work_sem': round(hours_all * random.uniform(0.2, 0.5), 2),
                    'history_work_month': round(hours_all * random.uniform(0.05, 0.15), 2),
                    'history_work_week': round(random.uniform(0, 20), 2),
                    'top_view': top_view,
                }
            )

            if (i + 1) % 50 == 0:
                self.stdout.write(f'  Создано {i + 1}/300...')

        self.stdout.write(self.style.SUCCESS('ГОТОВО! Создано 300 студентов'))