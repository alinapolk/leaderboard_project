from rest_framework import generics
from LeaderBoard.selectors import get_all_teams
from LeaderBoard.serializers import TeamsSerializer, TeamDetailSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(get=extend_schema(tags=['teams'], summary='Список команд'))
class TeamListView(generics.ListAPIView):
    """Список всех команд"""
    serializer_class = TeamsSerializer

    def get_queryset(self):
        return get_all_teams()


@extend_schema_view(get=extend_schema(tags=['teams'], summary='Данные команды'))
class TeamDetailView(generics.RetrieveAPIView):
    """Данные одной команды с участниками"""
    serializer_class = TeamDetailSerializer
    lookup_field = 'team_id'

    def get_queryset(self):
        return get_all_teams()
