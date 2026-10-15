from rest_framework import generics
from LeaderBoard.selectors import get_all_projects
from LeaderBoard.serializers import ProjectsSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(get=extend_schema(tags=['projects'], summary='Список проектов'))
class ProjectListView(generics.ListAPIView):
    """Список всех проектов"""
    serializer_class = ProjectsSerializer

    def get_queryset(self):
        return get_all_projects()


@extend_schema_view(get=extend_schema(tags=['projects'], summary='Данные проекта'))
class ProjectDetailView(generics.RetrieveAPIView):
    """Данные одного проекта"""
    serializer_class = ProjectsSerializer
    lookup_field = 'id_project'

    def get_queryset(self):
        return get_all_projects()
