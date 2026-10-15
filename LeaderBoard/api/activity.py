from rest_framework import generics
from LeaderBoard.selectors import get_all_activity
from LeaderBoard.serializers import StudentActivitySerializer
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(get=extend_schema(tags=['activity'], summary='Список активности'))
class ActivityListView(generics.ListAPIView):
    """Все записи активности"""
    serializer_class = StudentActivitySerializer

    def get_queryset(self):
        return get_all_activity()
