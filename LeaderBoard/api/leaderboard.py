from urllib.parse import unquote
from rest_framework import generics
from LeaderBoard.selectors import get_leaderboard_students, get_leaderboard_projects
from LeaderBoard.serializers import StudentLeaderBoardSerializer, ProjectLeaderBoardSerializer


class StudentLeaderBoardListView(generics.ListAPIView):
    """
    Отдаёт топ-50 студентов ИШИТР, отсортированных по рейтингу.

    Параметры:
    ?search=иванов — поиск по ФИО
    """
    serializer_class = StudentLeaderBoardSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        if search:
            search = unquote(search)
        return get_leaderboard_students(search=search)


class ProjectLeaderBoardListView(generics.ListAPIView):
    """Рейтинг всех проектов"""
    serializer_class = ProjectLeaderBoardSerializer

    def get_queryset(self):
        return get_leaderboard_projects()