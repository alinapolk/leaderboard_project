from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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

    def get_queryset(self):
        return get_all_students()


class StudentsDetailView(generics.RetrieveAPIView):
    """Данные одного студента"""
    serializer_class = StudentsSerializer
    lookup_field = 'login'

    def get_queryset(self):
        return get_all_students()


class StudentsTeamsListView(generics.ListAPIView):
    """Команды студента"""
    serializer_class = StudentTeamSerializer

    def get_queryset(self):
        login = self.kwargs['login']
        return get_student_teams(login)


class StudentActivityView(generics.ListAPIView):
    """Активность студента"""
    serializer_class = StudentActivitySerializer

    def get_queryset(self):
        login = self.kwargs['login']
        return get_student_activity(login)


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