from rest_framework import generics
from LeaderBoard.selectors import get_all_teams
from LeaderBoard.serializers import TeamsSerializer, TeamDetailSerializer


class TeamListView(generics.ListAPIView):
    """Список всех команд"""
    serializer_class = TeamsSerializer

    def get_queryset(self):
        return get_all_teams()


class TeamDetailView(generics.RetrieveAPIView):
    """Данные одной команды с участниками"""
    serializer_class = TeamDetailSerializer
    lookup_field = 'team_id'

    def get_queryset(self):
        return get_all_teams()