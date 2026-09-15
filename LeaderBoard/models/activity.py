from django.db import models
from .team import Teams
from .student import Students


class Student_Teams(models.Model):
    """Связующая таблица Students in Teams (многие-ко-многим)"""
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


class Student_Activity(models.Model):
    """Таблица активности студентов в командах"""
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