from rest_framework import serializers
from LeaderBoard.models import Students, Projects
from LeaderBoard.common.utils import get_full_name


class StudentLeaderBoardSerializer(serializers.ModelSerializer):
    """Сериализатор для страницы рейтинга студентов"""
    full_name = serializers.SerializerMethodField()
    total_medals = serializers.SerializerMethodField()

    class Meta:
        model = Students
        fields = [
            'login',
            'full_name',
            'student_group',
            'top_view',
            'history_work_all',
            'history_work_sem',
            'history_work_month',
            'history_work_week',
            'study_score',
            'total_medals',
            'rating_score',
            'rating_score_week',
            'rating_score_month',
            'rating_score_sem',
        ]

    def get_full_name(self, obj):
        return get_full_name(obj.last_name, obj.first_name, obj.patronymic)

    def get_total_medals(self, obj):
        return obj.student_medals_set.count()


class ProjectLeaderBoardSerializer(serializers.ModelSerializer):
    """Сериализатор для рейтинга проектов"""
    total_hours = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    team_id = serializers.SerializerMethodField()

    class Meta:
        model = Projects
        fields = [
            'id_project',
            'project_name',
            'project_type',
            'status',
            'category',
            'is_promoted',
            'total_hours',
            'members_count',
            'team_id',
        ]

    def get_total_hours(self, obj):
        team = obj.teams_set.first()
        if team:
            from django.db.models import Sum
            from LeaderBoard.models import Student_Activity
            result = Student_Activity.objects.filter(team=team).aggregate(total=Sum('hours_weekly'))
            return result['total'] or 0
        return 0

    def get_members_count(self, obj):
        team = obj.teams_set.first()
        return team.student_teams_set.count() if team else 0

    def get_team_id(self, obj):
        team = obj.teams_set.first()
        return team.team_id if team else None