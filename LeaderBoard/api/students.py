from rest_framework import generics
from LeaderBoard.selectors import (
    get_all_students,
    get_student_teams,
    get_student_activity
)
from LeaderBoard.models import Student_Medals
from LeaderBoard.serializers import (
    StudentsSerializer,
    StudentTeamSerializer,
    StudentActivitySerializer,
    StudentMedalSerializer
)


class StudentsListView(generics.ListAPIView):
    """Список всех студентов"""
    serializer_class = StudentsSerializer

    def get_queryset(self):
        return get_all_students()


class StudentsDetailView(generics.RetrieveAPIView):
    """Данные одного студента"""
    serializer_class = StudentsSerializer
    lookup_field = 'login'

    def get_queryset(self):
        return get_all_students()


class StudentsTeamsListView(generics.ListAPIView):
    """Команды студента"""
    serializer_class = StudentTeamSerializer

    def get_queryset(self):
        login = self.kwargs['login']
        return get_student_teams(login)


class StudentActivityView(generics.ListAPIView):
    """Активность студента"""
    serializer_class = StudentActivitySerializer

    def get_queryset(self):
        login = self.kwargs['login']
        return get_student_activity(login)


class StudentMedalsView(generics.ListAPIView):
    """Медали студента"""
    serializer_class = StudentMedalSerializer

    def get_queryset(self):
        login = self.kwargs['login']
        return Student_Medals.objects.filter(student_id=login)