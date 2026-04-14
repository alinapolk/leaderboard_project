from django.urls import path
from . import views

app_name = 'LeaderBoard'

urlpatterns = [
    # ЭНДПОИНТЫ ДЛЯ СТУДЕНТОВ
    path('api/students/', views.StudentsListView.as_view(), name='student_list'),
    path('api/students/<str:login>/', views.StudentsDetailView.as_view(), name='student_detail'),
    path('api/students/<str:login>/teams/', views.StudentsTeamsListView.as_view(), name='student_teams'),
    path('api/students/<str:login>/activity/', views.StudentActivityView.as_view(), name='student_activity'),
    path('api/students/<str:login>/medals/', views.StudentMedalsView.as_view(), name='student_medals'),

    # ЭНДПОИНТЫ ДЛЯ ПРОЕКТОВ
    path('api/projects/', views.ProjectListView.as_view(), name='project_list'),
    path('api/projects/<int:id_project>/', views.ProjectDetailView.as_view(), name='project_detail'),

    # ЭНДПОИНТЫ ДЛЯ КОМАНД
    path('api/teams/', views.TeamListView.as_view(), name='team_list'),
    path('api/teams/<int:team_id>/', views.TeamDetailView.as_view(), name='team_detail'),

    # ЭНДПОИНТЫ ДЛЯ АКТИВНОСТИ
    path('api/activity/', views.ActivityListView.as_view(), name='activity_list'),

    # ЭНДПОИНТЫ ДЛЯ РЕЙТИНГА
    path('api/leaderboard/students/', views.StudentLeaderBoardListView.as_view(), name='leaderboard_students'),
    path('api/leaderboard/projects/', views.ProjectLeaderBoardListView.as_view(), name='leaderboard_projects'),
]