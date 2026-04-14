from django.db import models


# 1. Таблица студентов
class Students(models.Model):
    login = models.CharField(primary_key=True, max_length=50)
    someone_id = models.CharField(max_length=50, unique=True) # ID из API вуза для интеграции
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100, blank=True, null=True)
    student_group = models.CharField(max_length=20)
    direction_name = models.CharField(max_length=100)
    study_year = models.IntegerField(blank=True, null=True)
    faculty = models.CharField(max_length=100)
    study_score = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    debt_count = models.IntegerField(blank=True, null=True)
    history_work_sem = models.DecimalField(max_digits=8, decimal_places=2, default=0) # Часы за семестр для быстрого
    # рейтинга
    history_work_week = models.DecimalField(max_digits=6, decimal_places=2, default=0) # Часы за неделю для быстрого
    # рейтинга
    history_work_all = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Всего часов за всё время
    history_work_month = models.DecimalField(max_digits=8, decimal_places=2, default=0) # Часы за месяц для быстрого
    # рейтинга
    top_view = models.CharField(max_length=100, blank=True, null=True) # Для категоризации студентов (лидер, активный,
    # новичок и т.д.)


    class Meta:
        db_table = 'students'


# 2. Таблица проектов
class Projects(models.Model):
    id_project = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    info_akadem = models.TextField(blank=True, null=True) # Информация об академах/переводах для анализа отсева

    class Meta:
        db_table = 'projects'


# 3. Таблица команд
class Teams(models.Model):
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


# 4. Связующая таблица Students in Teams (многие-ко-многим)
class Student_Teams(models.Model):
    ROLE_CHOICES = [
        ('Студент', 'Студент'),
        ('Наставник', 'Наставник'),
    ]
    team = models.ForeignKey(
        Teams,
        on_delete=models.CASCADE,
        db_column='team_id'
    )
    student = models.ForeignKey(
        Students,
        on_delete=models.CASCADE,
        db_column='student_login'
    )
    rol = models.CharField(max_length=20, choices=ROLE_CHOICES)
    joined_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_teams'
        constraints = [
            models.UniqueConstraint(
                fields=['team', 'student'],
                name='unique_team_student'
            )
        ]


# 5. Таблица активности студентов в командах
class Student_Activity(models.Model):
    activity_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Students,
        on_delete=models.CASCADE,
        db_column='student_login'
    )
    team = models.ForeignKey(
        Teams,
        on_delete=models.CASCADE,
        db_column='team_id'
    )
    hours_weekly = models.DecimalField(max_digits=4, decimal_places=1)
    weekly_period = models.DateField()

    class Meta:
        db_table = 'student_activity'
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'team', 'weekly_period'],
                name='unique_student_team_week'
            ),
            models.CheckConstraint(
                condition=models.Q(hours_weekly__gte=0),
                name='hours_weekly_non_negative'
            )
        ]


# 6. Таблица медалей студентов
class Student_Medals(models.Model):
    medal_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Students,
        on_delete=models.CASCADE,
        db_column='student_login'
    )
    grade = models.IntegerField()
    medal_name = models.CharField(max_length=100)
    award_date = models.DateField()

    class Meta:
        db_table = 'student_medals'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(grade__gte=1),
                name='grade_gte_1'
            )
        ]