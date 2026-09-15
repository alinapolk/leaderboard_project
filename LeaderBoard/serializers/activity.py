from rest_framework import serializers
from LeaderBoard.models import Student_Activity


class StudentActivitySerializer(serializers.ModelSerializer):
    """Сериализатор для Student_Activity"""

    student_full_name = serializers.SerializerMethodField()
    team_name = serializers.CharField(
        source='team.project.project_name',
        read_only=True
    )

    class Meta:
        model = Student_Activity
        fields = [
            'activity_id',
            'student',
            'student_full_name',
            'team',
            'team_name',
            'hours_weekly',
            'weekly_period',
        ]

    def get_student_full_name(self, obj):
        """Формируем ФИО студента"""
        s = obj.student
        parts = [s.last_name, s.first_name]
        if s.patronymic:
            parts.append(s.patronymic)
        return ' '.join(parts)