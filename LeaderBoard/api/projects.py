from rest_framework import generics
from LeaderBoard.selectors import get_all_projects
from LeaderBoard.serializers import ProjectsSerializer


class ProjectListView(generics.ListAPIView):
    """Список всех проектов"""
    serializer_class = ProjectsSerializer

    def get_queryset(self):
        return get_all_projects()


class ProjectDetailView(generics.RetrieveAPIView):
    """Данные одного проекта"""
    serializer_class = ProjectsSerializer
    lookup_field = 'id_project'

    def get_queryset(self):
        return get_all_projects()