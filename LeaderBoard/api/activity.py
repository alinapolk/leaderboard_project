from rest_framework import generics
from LeaderBoard.selectors import get_all_activity
from LeaderBoard.serializers import StudentActivitySerializer


class ActivityListView(generics.ListAPIView):
    """Все записи активности"""
    serializer_class = StudentActivitySerializer

    def get_queryset(self):
        return get_all_activity()