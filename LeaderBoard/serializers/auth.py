from rest_framework import serializers
from django.contrib.auth.models import User
from LeaderBoard.models import Students
from .students import StudentShortSerializer

class LoginSerializer(serializers.Serializer):
    """Принимаем логин и пароль"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ConsentSerializer(serializers.Serializer):
    """Принимаем решение по согласию"""
    consent = serializers.BooleanField()
    temp_token = serializers.CharField()


class UserInfoSerializer(serializers.ModelSerializer):
    """Отдатет информацию о пользователе"""
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'role'
        ]

    def get_full_name(self, obj):
        parts = [obj.first_name, obj.last_name]
        return ' '.join(filter(None, parts)) or obj.username

    def get_role(self, obj):
        if obj.is_superuser:
            return 'admin'
        if obj.groups.filter(name='manager').exists():
            return 'manager'
        return 'student'


class MeSerializer(serializers.Serializer):
    """Полная информация о текущем пользователе"""

    def to_representation(self, instance):
        # Данные пользователя
        user_data = UserInfoSerializer(instance).data

        # Данные студента
        try:
            student = Students.objects.get(user=instance)
            student_data = StudentShortSerializer(student).data
        except Students.DoesNotExist:
            student_data = None

        # Статус согласия
        try:
            consent_given = instance.userconsent.is_given
        except:
            consent_given = False

        return {
            'user': user_data,
            'student': student_data,
            'consent_given': consent_given
        }