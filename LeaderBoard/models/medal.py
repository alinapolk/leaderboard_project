from django.db import models
from .student import Students


class Student_Medals(models.Model):
    """Таблица медалей студентов"""
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