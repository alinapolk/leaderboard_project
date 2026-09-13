from django.core.management.base import BaseCommand
from django.db import transaction
from LeaderBoard.models import Students
import random


class Command(BaseCommand):
    help = 'Заполняет базу 2000 тестовыми студентами'

    def handle(self, *args, **kwargs):
        # Списки для генерации
        first_names_m = ['Александр', 'Дмитрий', 'Иван', 'Артём', 'Виталий',
                         'Евгений', 'Андрей', 'Даниил', 'Максим', 'Никита',
                         'Сергей', 'Павел', 'Роман', 'Владислав', 'Кирилл',
                         'Михаил', 'Антон', 'Глеб', 'Илья', 'Ярослав',
                         'Тимофей', 'Матвей', 'Лев', 'Егор', 'Фёдор',
                         'Георгий', 'Константин', 'Олег', 'Виктор', 'Денис']

        first_names_f = ['Александра', 'Мария', 'Анна', 'Екатерина', 'Дарья',
                         'София', 'Анастасия', 'Виктория', 'Полина', 'Ксения',
                         'Елизавета', 'Валерия', 'Алёна', 'Юлия', 'Ольга',
                         'Татьяна', 'Наталья', 'Светлана', 'Маргарита', 'Арина',
                         'Вероника', 'Милана', 'Алиса', 'Кристина', 'Инна',
                         'Людмила', 'Галина', 'Валентина', 'Жанна', 'Регина']

        last_names_m = ['Волков', 'Соколов', 'Петров', 'Кузнецов', 'Смирнов',
                        'Новиков', 'Лаврентьев', 'Филатов', 'Юрченко', 'Киселев',
                        'Иванов', 'Попов', 'Зайцев', 'Белов', 'Титов',
                        'Морозов', 'Лебедев', 'Егоров', 'Павлов', 'Козлов',
                        'Степанов', 'Николаев', 'Орлов', 'Андреев', 'Макаров',
                        'Никитин', 'Захаров', 'Зайцев', 'Соловьёв', 'Борисов']

        last_names_f = ['Волкова', 'Соколова', 'Петрова', 'Кузнецова', 'Смирнова',
                        'Новикова', 'Лаврентьева', 'Филатова', 'Юрченко', 'Киселева',
                        'Иванова', 'Попова', 'Зайцева', 'Белова', 'Титова',
                        'Морозова', 'Лебедева', 'Егорова', 'Павлова', 'Козлова',
                        'Степанова', 'Николаева', 'Орлова', 'Андреева', 'Макарова',
                        'Никитина', 'Захарова', 'Соловьёва', 'Борисова', 'Виноградова']

        patronymics_m = ['Сергеевич', 'Андреевич', 'Иванович', 'Петрович',
                         'Дмитриевич', 'Александрович', 'Николаевич',
                         'Владимирович', 'Игоревич', 'Павлович',
                         'Максимович', 'Олегович', 'Викторович', 'Денисович',
                         'Константинович', 'Георгиевич', 'Фёдорович', 'Львович']

        patronymics_f = ['Сергеевна', 'Андреевна', 'Ивановна', 'Петровна',
                         'Дмитриевна', 'Александровна', 'Николаевна',
                         'Владимировна', 'Игоревна', 'Павловна',
                         'Максимовна', 'Олеговна', 'Викторовна', 'Денисовна',
                         'Константиновна', 'Георгиевна', 'Фёдоровна', 'Львовна']

        groups = [
            '8ВМ01', '8ВМ02', '8ВМ11', '8ВМ12', '8ВМ21', '8ВМ22',
            '8ВМ31', '8ВМ32', '8ВМ41', '8ВМ42', '8ВМ51', '8ВМ52',
            '8ИС01', '8ИС02', '8ИС11', '8ИС12', '8ПИ01', '8ПИ02',
            '8РТ01', '8РТ02'
        ]
        directions = [
            'Программная инженерия', 'Информационные системы',
            'Прикладная информатика', 'Робототехника',
            'Информатика и вычислительная техника',
            'Автоматизация технологических процессов'
        ]
        statuses = ['лидер', 'лидер', 'активный', 'активный', 'активный',
                    'новичок', 'новичок', 'новичок', 'новичок', 'новичок']

        self.stdout.write('Удаляю старые записи...')
        deleted, _ = Students.objects.all().delete()
        self.stdout.write(self.style.WARNING(f'Удалено {deleted} записей'))

        self.stdout.write('Создаю 2000 студентов...')

        students_to_create = []
        seen_logins = set()

        for i in range(2000):
            # Генерация уникального логина
            attempts = 0
            while True:
                is_male = random.choice([True, False])
                if is_male:
                    last_name = random.choice(last_names_m)
                else:
                    last_name = random.choice(last_names_f)

                login = f"{last_name.lower()[:6]}{i+1:04d}"
                if login not in seen_logins:
                    seen_logins.add(login)
                    break
                attempts += 1
                if attempts > 100:
                    login = f"student{i+1:04d}"
                    seen_logins.add(login)
                    break

            # Имя и отчество в зависимости от пола
            if is_male:
                first_name = random.choice(first_names_m)
                patronymic = random.choice(patronymics_m)
            else:
                first_name = random.choice(first_names_f)
                patronymic = random.choice(patronymics_f)

            # study_score от 0 до 1 с шагом 0.01
            study_score = round(random.uniform(1, 5), 2)
            # Часы: нормальное распределение
            hours = int(random.gauss(250, 150))
            hours = max(0, min(hours, 800))

            data = {
                'login': login,
                'someone_id': f'tpu-{login}',
                'first_name': first_name,
                'last_name': last_name,
                'patronymic': patronymic,
                'student_group': random.choice(groups),
                'direction_name': random.choice(directions),
                'study_year': random.randint(1, 4),
                'faculty': 'ИШИТР',
                'study_score': study_score,
                'debt_count': random.choices([0, 1, 2, 3, 4], weights=[60, 20, 10, 5, 5])[0],
                'history_work_all': hours,
                'history_work_sem': int(hours * random.uniform(0.2, 0.5)),
                'history_work_month': int(hours * random.uniform(0.05, 0.15)),
                'history_work_week': int(hours * random.uniform(0.01, 0.05)),
                'top_view': random.choice(statuses),
                'rating_score': 0.0,  # Будет пересчитан сигналом
            }
            students_to_create.append(Students(**data))

        # Массовое создание (быстро)
        with transaction.atomic():
            Students.objects.bulk_create(students_to_create, batch_size=500)

        self.stdout.write(self.style.SUCCESS(
            f'ГОТОВО! Создано {Students.objects.count()} студентов'
        ))

        # Пересчитываем rating_score для всех
        self.stdout.write('Пересчитываю рейтинг...')
        from LeaderBoard.tasks import recalculate_ratings
        recalculate_ratings()  # вызываем напрямую, не через .delay()

        self.stdout.write(self.style.SUCCESS('Рейтинг пересчитан'))