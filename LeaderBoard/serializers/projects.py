from rest_framework import serializers
from LeaderBoard.models import Projects


class ProjectsShortSerializer(serializers.ModelSerializer):
    """
    Короткий сериализатор для Projects
    Краткая информация по проекту
    """
    class Meta:
        model = Projects
        fields = [
            'id_project',
            'project_name',
        ]

class ProjectsSerializer(serializers.ModelSerializer):
    """Полный сериализатор Projects"""

    team_info = serializers.SerializerMethodField()

    class Meta:
        model = Projects
        fields = [
            'id_project',
            'project_name',
            'description',
            'info_akadem',
            'team_info',
        ]

    def get_team_info(self, obj):
        """Получаем информацию о команде проекта"""
        team = obj.teams_set.first() # Берем первую команду
        if team:
            return {
                'team_id': team.team_id,
                'expert_score': team.expert_score,
                'period_start': team.period_start,
                'period_end': team.period_end,
                'members_count': team.student_teams_set.count(),
            }
        return None