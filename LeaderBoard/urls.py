from django.urls import path

from . import views
from .views_auth import LoginView, ConsentView, LogoutView, MeView, RefreshTokenView, MyRatingView

app_name = 'LeaderBoard'

urlpatterns = [
    # ============================================================
    # СТУДЕНТЫ
    # ============================================================
    path('students/', views.StudentsListView.as_view(), name='student_list'),
    path('students/<str:login>/', views.StudentsDetailView.as_view(), name='student_detail'),
    path('students/<str:login>/teams/', views.StudentsTeamsListView.as_view(), name='student_teams'),
    path('students/<str:login>/activity/', views.StudentActivityView.as_view(), name='student_activity'),
    path('students/<str:login>/medals/', views.StudentMedalsView.as_view(), name='student_medals'),

    # ============================================================
    # ПРОЕКТЫ
    # ============================================================
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/<int:id_project>/', views.ProjectDetailView.as_view(), name='project_detail'),

    # ============================================================
    # КОМАНДЫ
    # ============================================================
    path('teams/', views.TeamListView.as_view(), name='team_list'),
    path('teams/<int:team_id>/', views.TeamDetailView.as_view(), name='team_detail'),

    # ============================================================
    # АКТИВНОСТЬ
    # ============================================================
    path('activity/', views.ActivityListView.as_view(), name='activity_list'),

    # ============================================================
    # РЕЙТИНГ
    # ============================================================
    path('leaderboard/students/', views.StudentLeaderBoardListView.as_view(), name='leaderboard_students'),
    path('leaderboard/projects/', views.ProjectLeaderBoardListView.as_view(), name='leaderboard_projects'),

    # ============================================================
    # АВТОРИЗАЦИЯ
    # ============================================================
    path('auth/login/', LoginView.as_view(), name='auth_login'),
    path('auth/consent/', ConsentView.as_view(), name='auth_consent'),
    path('auth/me/', MeView.as_view(), name='auth_me'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='auth_refresh'),
    path('auth/me/rating/', MyRatingView.as_view(), name='my_rating'),
]