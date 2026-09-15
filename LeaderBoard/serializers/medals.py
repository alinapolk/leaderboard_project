from rest_framework import serializers
from LeaderBoard.models import Student_Medals

class StudentMedalSerializer(serializers.ModelSerializer):
    """Сериализатор для Student_Medal"""

    student_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Student_Medals
        fields = [
            'medal_id',
            'student',
            'student_full_name',
            'grade',
            'medal_name',
            'award_date',
        ]

    def get_student_full_name(self, obj):
        """Формируем ФИО студента"""
        s = obj.student
        parts = [s.last_name, s.first_name]
        if obj.patronymic:
            parts.append(obj.patronymic)
        return ' '.join(parts)