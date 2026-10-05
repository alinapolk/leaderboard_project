from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view

from LeaderBoard.selectors import (
    get_all_students,
    get_student_teams,
    get_student_activity
)
from LeaderBoard.models import Student_Medals
from LeaderBoard.serializers import (
    StudentsSerializer,
    StudentTeamSerializer,
    StudentActivitySerializer,
    StudentMedalSerializer
)
from LeaderBoard.services import get_student_rating_history


class StudentsListView(generics.ListAPIView):
    """Список всех студентов"""
    serializer_class = StudentsSerializer

    @extend_schema(
        tags=['students'], summary='Список студентов',
        description='Возвращает список студентов. Поддерживает поиск и фильтрацию по курсу и группе.',
        parameters=[
            OpenApiParameter('search', str, description='Поиск по фамилии, имени, отчеству или логину.'),
            OpenApiParameter('course', int, description='Номер курса (год обучения).'),
            OpenApiParameter('group', str, description='Учебная группа.'),
            OpenApiParameter('ordering', str, description='Сортировка по полю; префикс - задаёт обратный порядок.', enum=['login', '-login', 'study_year', '-study_year', 'study_score', '-study_score', 'rating_score', '-rating_score']),
        ],
        responses={200: OpenApiResponse(response=StudentsSerializer(many=True), examples=[OpenApiExample('Студенты', value=[{'login': 'student1', 'first_name': 'Иван', 'last_name': 'Иванов', 'student_group': '8ВМ01', 'study_year': 3, 'full_name': 'Иванов Иван'}])])},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = get_all_students()
        params = self.request.query_params
        search = params.get('search')
        if search:
            queryset = queryset.filter(
                Q(login__icontains=search) | Q(first_name__icontains=search) |
                Q(last_name__icontains=search) | Q(patronymic__icontains=search)
            )
        if params.get('course'):
            queryset = queryset.filter(study_year=params['course'])
        if params.get('group'):
            queryset = queryset.filter(student_group__iexact=params['group'])
        allowed_ordering = {'login', '-login', 'study_year', '-study_year', 'study_score', '-study_score', 'rating_score', '-rating_score'}
        ordering = params.get('ordering')
        if ordering in allowed_ordering:
            queryset = queryset.order_by(ordering)
        return queryset


class StudentsDetailView(generics.RetrieveAPIView):
    """Данные одного студента"""
    serializer_class = StudentsSerializer
    lookup_field = 'login'

    @extend_schema(
        tags=['students'], summary='Получить студента',
        description='Возвращает профиль студента по логину.',
        responses={200: OpenApiResponse(response=StudentsSerializer, examples=[OpenApiExample('Студент', value={'login': 'student1', 'first_name': 'Иван', 'last_name': 'Иванов', 'student_group': '8ВМ01', 'study_year': 3, 'full_name': 'Иванов Иван'})])},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return get_all_students()


@extend_schema_view(get=extend_schema(tags=['students'], summary='Команды студента'))
class StudentsTeamsListView(generics.ListAPIView):
    """Команды студента"""
    serializer_class = StudentTeamSerializer

    def get_queryset(self):
        login = self.kwargs['login']
        return get_student_teams(login)


@extend_schema_view(get=extend_schema(tags=['students'], summary='Активность студента'))
class StudentActivityView(generics.ListAPIView):
    """Активность студента"""
    serializer_class = StudentActivitySerializer

    def get_queryset(self):
        login = self.kwargs['login']
        return get_student_activity(login)


@extend_schema_view(get=extend_schema(tags=['students'], summary='Медали студента'))
class StudentMedalsView(generics.ListAPIView):
    """Медали студента"""
    serializer_class = StudentMedalSerializer

    def get_queryset(self):
        login = self.kwargs['login']
        return Student_Medals.objects.filter(student_id=login)


class StudentRatingHistoryView(APIView):
    """
    GET /api/students/{login}/rating/history/
    Возвращает историю рейтинга студента
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['students'], summary='История рейтинга студента',
        description='Возвращает последние снимки рейтинга студента; по умолчанию до 10 записей.',
        parameters=[OpenApiParameter('limit', int, description='Максимальное число записей истории.', required=False)],
        responses={200: OpenApiResponse(response=dict, examples=[OpenApiExample('История', value={'student_login': 'student1', 'history': [{'score': 120.5, 'study_score': 4.8, 'history_work_all': 200, 'study_component': 40, 'work_component': 80, 'formula_version': 'v1', 'reason': 'manual', 'created_at': '2026-10-05T12:00:00+00:00'}]})])},
    )
    def get(self, request, login):
        limit = int(request.query_params.get('limit', 10))
        history = get_student_rating_history(login, limit=limit)
        
        data = [{
            'score': float(snapshot.score),
            'study_score': float(snapshot.study_score) if snapshot.study_score else None,
            'history_work_all': float(snapshot.history_work_all) if snapshot.history_work_all else None,
            'study_component': float(snapshot.study_component) if snapshot.study_component else None,
            'work_component': float(snapshot.work_component) if snapshot.work_component else None,
            'formula_version': snapshot.formula_version,
            'reason': snapshot.reason,
            'created_at': snapshot.created_at.isoformat(),
        } for snapshot in history]
        
        return Response({
            'student_login': login,
            'history': data
        })
