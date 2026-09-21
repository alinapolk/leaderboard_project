from urllib.parse import unquote
from rest_framework import generics
from LeaderBoard.selectors import get_leaderboard_students, get_leaderboard_projects
from LeaderBoard.serializers import StudentLeaderBoardSerializer, ProjectLeaderBoardSerializer
from LeaderBoard.services.rating_service import AVAILABLE_PERIODS


class StudentLeaderBoardListView(generics.ListAPIView):
    """
    Отдаёт топ-50 студентов, отсортированных по рейтингу.

    Параметры:
    ?search=иванов — поиск по ФИО
    ?period=week|month|sem|all — период рейтинга (по умолчанию all)
    """
    serializer_class = StudentLeaderBoardSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        if search:
            search = unquote(search)

        period = self.request.query_params.get('period', 'all')
        if period not in AVAILABLE_PERIODS:
            period = 'all'

        return get_leaderboard_students(search=search, period=period)


class ProjectLeaderBoardListView(generics.ListAPIView):
    """Рейтинг всех проектов"""
    serializer_class = ProjectLeaderBoardSerializer

    def get_queryset(self):
        return get_leaderboard_projects()