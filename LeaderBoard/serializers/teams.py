from rest_framework import serializers
from LeaderBoard.models import Student_Teams, Teams
from .projects import ProjectsShortSerializer
from .students import StudentShortSerializer


class TeamsSerializer(serializers.ModelSerializer):
    """Полный сериализатор Teams"""

    project = ProjectsShortSerializer(read_only=True)
    members_count = serializers.SerializerMethodField() # Количество участников

    class Meta:
        model = Teams
        fields = [
            'team_id',
            'project',
            'expert_score',
            'period_start',
            'period_end',
            'members_count',
        ]

    def get_members_count(self, obj):
        """Получение информации по количесву участников"""
        return obj.student_teams_set.count()

class TeamDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор Teams"""

    project = ProjectsShortSerializer(read_only=True)
    members = serializers.SerializerMethodField() # список участников

    class Meta:
        model = Teams
        fields = [
            'team_id',
            'project',
            'expert_score',
            'period_start',
            'period_end',
            'members',
        ]

    def get_members(self, obj):
        """Формирует список участников"""

        members_data = []
        for st in obj.student_teams_set.select_related('student').all():
            members_data.append({
                'student' : StudentShortSerializer(st.student).data,
                'role' : st.rol,
                'joined_date' : st.joined_date,
            })
        return members_data

class StudentTeamSerializer(serializers.ModelSerializer):
    """Сериализатор для промежуточной таблицы Student_Teams"""

    student = StudentShortSerializer(read_only=True)
    team_name = serializers.CharField( # название команды = название проекта
        source='team.project.project_name',
        read_only=True
    )
    team_id = serializers.IntegerField(
        source='team.team_id',
        read_only=True
    )

    class Meta:
        model = Student_Teams
        fields = [
            'student',
            'team_id',
            'team_name',
            'rol',
            'joined_date',
        ]