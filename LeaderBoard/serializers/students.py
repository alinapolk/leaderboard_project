from rest_framework import serializers
from LeaderBoard.models import Students
from LeaderBoard.common.utils import get_full_name


class StudentsSerializer(serializers.ModelSerializer):
    """Полный сериализатор для Students"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Students
        fields = [
            'login',
            'someone_id',
            'first_name',
            'last_name',
            'patronymic',
            'student_group',
            'direction_name',
            'study_year',
            'faculty',
            'study_score',
            'debt_count',
            'top_view',
            'history_work_sem',
            'history_work_week',
            'history_work_all',
            'history_work_month',
            'full_name',
        ]

    def get_full_name(self, obj):
        return get_full_name(obj.last_name, obj.first_name, obj.patronymic)


class StudentShortSerializer(serializers.ModelSerializer):
    """Короткий сериализатор для Students"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Students
        fields = [
            'login',
            'full_name',
            'student_group',
            'top_view',
            'history_work_sem',
        ]

    def get_full_name(self, obj):
        return get_full_name(obj.last_name, obj.first_name, obj.patronymic)