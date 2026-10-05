from urllib.parse import unquote
from rest_framework import generics
from LeaderBoard.selectors import get_leaderboard_students, get_leaderboard_projects
from LeaderBoard.serializers import StudentLeaderBoardSerializer, ProjectLeaderBoardSerializer
from LeaderBoard.services.rating_service import AVAILABLE_PERIODS
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema


class StudentLeaderBoardListView(generics.ListAPIView):
    """
    Отдаёт топ-50 студентов, отсортированных по рейтингу.

    Параметры:
    ?search=иванов — поиск по ФИО
    ?period=week|month|sem|all — период рейтинга (по умолчанию all)
    """
    serializer_class = StudentLeaderBoardSerializer

    @extend_schema(
        tags=['leaderboard'], summary='Рейтинг студентов',
        description='Возвращает до 50 студентов, отсортированных по рейтингу выбранного периода.',
        parameters=[
            OpenApiParameter('period', str, description='Период рейтинга.', enum=['week', 'month', 'sem', 'all']),
            OpenApiParameter('search', str, description='Поиск по фамилии, имени или отчеству.'),
        ],
        responses={200: OpenApiResponse(response=StudentLeaderBoardSerializer(many=True), examples=[OpenApiExample('Рейтинг студентов', value=[{'login': 'student1', 'full_name': 'Иванов Иван', 'student_group': '8ВМ01', 'rating_score': 120.5, 'total_medals': 2}])])},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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

    @extend_schema(
        tags=['leaderboard'], summary='Рейтинг проектов',
        description='Возвращает проекты в порядке приоритета и названия.',
        responses={200: OpenApiResponse(response=ProjectLeaderBoardSerializer(many=True), examples=[OpenApiExample('Проекты', value=[{'id_project': 1, 'project_name': 'Пример проекта', 'project_type': 'research', 'total_hours': 120, 'members_count': 4, 'team_id': 1}])])},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return get_leaderboard_projects()
