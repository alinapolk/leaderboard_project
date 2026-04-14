from rest_framework import generics
from .models import Students, Projects, Teams, Student_Teams, Student_Activity, Student_Medals
from .serializers import (StudentsSerializer, ProjectsSerializer, TeamsSerializer, TeamDetailSerializer,
                          StudentTeamSerializer, StudentActivitySerializer, StudentMedalSerializer,
                          StudentLeaderBoardSerializer, ProjectLeaderBoardSerializer)

class StudentsListView(generics.ListAPIView):
    """Список всех студентов"""
    queryset = Students.objects.all()
    serializer_class = StudentsSerializer

class StudentsDetailView(generics.RetrieveAPIView):
    """Данный одного студента"""
    queryset = Students.objects.all()
    serializer_class = StudentsSerializer
    lookup_field = 'login'

class StudentsTeamsListView(generics.ListAPIView):
    """Команды студента"""
    serializer_class = StudentTeamSerializer

    def get_queryset(self):
        login = self.kwargs['login']
        return Student_Teams.objects.filter(student_id=login)

class StudentMedalsView(generics.ListAPIView):
    """Медали студента"""
    serializer_class = StudentMedalSerializer

    def get_queryset(self):
        login = self.kwargs['login']
        return Student_Medals.objects.filter(student_id=login)

class StudentActivityView(generics.ListAPIView):
    """Активность студента"""
    serializer_class = StudentActivitySerializer

    def get_queryset(self):
        login = self.kwargs['login']
        return Student_Activity.objects.filter(student_id=login)

class ProjectListView(generics.ListAPIView):
    """Список всех проектов"""
    queryset = Projects.objects.all()
    serializer_class = ProjectsSerializer

class ProjectDetailView(generics.RetrieveAPIView):
    """Данные одного проекта"""
    queryset = Projects.objects.all()
    serializer_class = ProjectsSerializer
    lookup_field = 'id_project'

class TeamListView(generics.ListAPIView):
    """Список всех команд"""
    queryset = Teams.objects.all()
    serializer_class = TeamsSerializer

class TeamDetailView(generics.RetrieveAPIView):
    """Данные одной команды с участниками"""
    queryset = Teams.objects.all()
    serializer_class = TeamDetailSerializer
    lookup_field = 'team_id'

class ActivityListView(generics.ListAPIView):
    """Все записи активности"""
    queryset = Student_Activity.objects.all()
    serializer_class = StudentActivitySerializer

class StudentLeaderBoardListView(generics.ListAPIView):
    """Топ-10 студентов по часам"""
    queryset = Students.objects.filter(
        history_work_all__gt=0
    ).order_by('-history_work_all')[:10]
    serializer_class = StudentLeaderBoardSerializer

class ProjectLeaderBoardListView(generics.ListAPIView):
    """Рейтинг всех проектов"""
    queryset = Projects.objects.all()
    serializer_class = ProjectLeaderBoardSerializer