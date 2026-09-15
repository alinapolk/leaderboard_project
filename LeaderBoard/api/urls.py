from django.urls import path
from . import students, projects, teams, activity, leaderboard, auth

app_name = 'LeaderBoard'

urlpatterns = [
    # СТУДЕНТЫ
    path('students/', students.StudentsListView.as_view(), name='student_list'),
    path('students/<str:login>/', students.StudentsDetailView.as_view(), name='student_detail'),
    path('students/<str:login>/teams/', students.StudentsTeamsListView.as_view(), name='student_teams'),
    path('students/<str:login>/activity/', students.StudentActivityView.as_view(), name='student_activity'),
    path('students/<str:login>/medals/', students.StudentMedalsView.as_view(), name='student_medals'),

    # ПРОЕКТЫ
    path('projects/', projects.ProjectListView.as_view(), name='project_list'),
    path('projects/<int:id_project>/', projects.ProjectDetailView.as_view(), name='project_detail'),

    # КОМАНДЫ
    path('teams/', teams.TeamListView.as_view(), name='team_list'),
    path('teams/<int:team_id>/', teams.TeamDetailView.as_view(), name='team_detail'),

    # АКТИВНОСТЬ
    path('activity/', activity.ActivityListView.as_view(), name='activity_list'),

    # РЕЙТИНГ
    path('leaderboard/students/', leaderboard.StudentLeaderBoardListView.as_view(), name='leaderboard_students'),
    path('leaderboard/projects/', leaderboard.ProjectLeaderBoardListView.as_view(), name='leaderboard_projects'),

    # АВТОРИЗАЦИЯ
    path('auth/login/', auth.LoginView.as_view(), name='auth_login'),
    path('auth/consent/', auth.ConsentView.as_view(), name='auth_consent'),
    path('auth/me/', auth.MeView.as_view(), name='auth_me'),
    path('auth/logout/', auth.LogoutView.as_view(), name='auth_logout'),
    path('auth/refresh/', auth.RefreshTokenView.as_view(), name='auth_refresh'),
    path('auth/me/rating/', auth.MyRatingView.as_view(), name='my_rating'),
]