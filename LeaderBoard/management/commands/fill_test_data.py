from django.core.management.base import BaseCommand
from LeaderBoard.models import Students

class Command(BaseCommand):
    help = 'Заполняет базу тестовыми студентами'

    def handle(self, *args, **kwargs):
        students_data = [
            {'login': 'aks21', 'someone_id': 'tpu-aks21', 'first_name': 'Александра', 'last_name': 'Волкова', 'patronymic': 'Сергеевна', 'student_group': '8ВМ01', 'direction_name': 'Программная инженерия', 'study_year': 3, 'faculty': 'ИШИТР', 'study_score': 4.8, 'debt_count': 0, 'history_work_all': 450, 'top_view': 'лидер'},
            {'login': 'a85i', 'someone_id': 'tpu-a85i', 'first_name': 'Дмитрий', 'last_name': 'Соколов', 'patronymic': 'Андреевич', 'student_group': '8ВМ02', 'direction_name': 'Программная инженерия', 'study_year': 3, 'faculty': 'ИШИТР', 'study_score': 4.7, 'debt_count': 0, 'history_work_all': 420, 'top_view': 'лидер'},
            {'login': 'aks31', 'someone_id': 'tpu-aks31', 'first_name': 'Мария', 'last_name': 'Петрова', 'patronymic': 'Ивановна', 'student_group': '8ВМ11', 'direction_name': 'Программная инженерия', 'study_year': 2, 'faculty': 'ИШИТР', 'study_score': 4.9, 'debt_count': 0, 'history_work_all': 380, 'top_view': 'активный'},
            {'login': 'ajs1', 'someone_id': 'tpu-ajs1', 'first_name': 'Иван', 'last_name': 'Кузнецов', 'patronymic': 'Петрович', 'student_group': '8ВМ01', 'direction_name': 'Программная инженерия', 'study_year': 4, 'faculty': 'ИШИТР', 'study_score': 4.6, 'debt_count': 1, 'history_work_all': 350, 'top_view': 'активный'},
            {'login': 'ajs2', 'someone_id': 'tpu-ajs2', 'first_name': 'Анна', 'last_name': 'Смирнова', 'patronymic': 'Дмитриевна', 'student_group': '8ВМ02', 'direction_name': 'Программная инженерия', 'study_year': 2, 'faculty': 'ИШИТР', 'study_score': 4.5, 'debt_count': 0, 'history_work_all': 320, 'top_view': 'активный'},
            {'login': 'aks32', 'someone_id': 'tpu-aks32', 'first_name': 'Артём', 'last_name': 'Новиков', 'patronymic': 'Александрович', 'student_group': '8ВМ11', 'direction_name': 'Программная инженерия', 'study_year': 3, 'faculty': 'ИШИТР', 'study_score': 4.4, 'debt_count': 0, 'history_work_all': 290, 'top_view': 'активный'},
            {'login': 'aks33', 'someone_id': 'tpu-aks33', 'first_name': 'Виталий', 'last_name': 'Лаврентьев', 'patronymic': 'Сергеевич', 'student_group': '8ВМ01', 'direction_name': 'Программная инженерия', 'study_year': 4, 'faculty': 'ИШИТР', 'study_score': 4.3, 'debt_count': 2, 'history_work_all': 260, 'top_view': 'новичок'},
            {'login': 'aks34', 'someone_id': 'tpu-aks34', 'first_name': 'Евгений', 'last_name': 'Филатов', 'patronymic': 'Николаевич', 'student_group': '8ВМ02', 'direction_name': 'Программная инженерия', 'study_year': 3, 'faculty': 'ИШИТР', 'study_score': 4.2, 'debt_count': 0, 'history_work_all': 230, 'top_view': 'новичок'},
            {'login': 'aks35', 'someone_id': 'tpu-aks35', 'first_name': 'Андрей', 'last_name': 'Юрченко', 'patronymic': 'Владимирович', 'student_group': '8ВМ11', 'direction_name': 'Программная инженерия', 'study_year': 2, 'faculty': 'ИШИТР', 'study_score': 4.1, 'debt_count': 0, 'history_work_all': 200, 'top_view': 'новичок'},
            {'login': 'aks36', 'someone_id': 'tpu-aks36', 'first_name': 'Даниил', 'last_name': 'Киселев', 'patronymic': 'Игоревич', 'student_group': '8ВМ01', 'direction_name': 'Программная инженерия', 'study_year': 3, 'faculty': 'ИШИТР', 'study_score': 4.0, 'debt_count': 1, 'history_work_all': 180, 'top_view': 'новичок'},
        ]

        for s in students_data:
            student, created = Students.objects.update_or_create(
                login=s['login'],
                defaults=s
            )
            status = 'Создан' if created else 'Обновлён'
            self.stdout.write(f'{status}: {student.full_name() if hasattr(student, "full_name") else student.first_name} {student.last_name}')

        self.stdout.write(self.style.SUCCESS(f'ГОТОВО! Добавлено {len(students_data)} студентов'))