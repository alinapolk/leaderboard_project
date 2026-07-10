from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Students, Student_Medals, Student_Teams, Student_Activity, Teams, Projects, UserConsent


class StudentsSerializer(serializers.ModelSerializer):
    """Полный сериализатор для Students"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Students # Указываем с какой моделью работаем
        fields = [
            'login',
            'someone_id',
            'first_name',
            'last_name',
            'patronymic',
            'student_group',
            'direction_name',
            'study_year',
            'faculty',
            'study_score',
            'debt_count',
            'top_view',

            # Поля для рейтинга
            'history_work_sem',
            'history_work_week',
            'history_work_all',
            'history_work_month',

            # Вычислиямое поле
            'full_name',
        ]

    def get_full_name(self, obj):
        """Формирует полное ФИО студента"""
        parts = [obj.last_name, obj.first_name]
        if obj.patronymic:
            parts.append(obj.patronymic)
        return ' '.join(parts)

class StudentShortSerializer(serializers.ModelSerializer):
    """
    Короткий сериализатор для Students
    Краткая информация по студентам
    """

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Students
        fields = [
            'login',
            'full_name',
            'student_group',
            'top_view',
            'history_work_sem',
        ]

    def get_full_name(self, obj):
        parts = [obj.last_name, obj.first_name]
        if obj.patronymic:
            parts.append(obj.patronymic)
        return ' '.join(parts)

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

class StudentActivitySerializer(serializers.ModelSerializer):
    """Сериализатор для Student_Activity"""

    student_full_name = serializers.SerializerMethodField()
    team_name = serializers.CharField(
        source='team.project.project_name',
        read_only=True
    )

    class Meta:
        model = Student_Activity
        fields = [
            'activity_id',
            'student',
            'student_full_name',
            'team',
            'team_name',
            'hours_weekly',
            'weekly_period',
        ]

    def get_student_full_name(self, obj):
        """Формируем ФИО студента"""
        s = obj.student
        parts = [s.last_name, s.first_name]
        if s.patronymic:
            parts.append(s.patronymic)
        return ' '.join(parts)

class StudentMedalSerializer(serializers.ModelSerializer):
    """Сериализатор для Student_Medal"""

    student_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Student_Medals
        fields = [
            'medal_id',
            'student',
            'student_full_name',
            'grade',
            'medal_name',
            'award_date',
        ]

    def get_student_full_name(self, obj):
        """Формируем ФИО студента"""
        s = obj.student
        parts = [s.last_name, s.first_name]
        if obj.patronymic:
            parts.append(obj.patronymic)
        return ' '.join(parts)

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
            'study_score',
            'total_medals',
        ]

    def get_full_name(self, obj):
        """Формируем ФИО студента"""
        parts = [obj.last_name, obj.first_name]
        if obj.patronymic:
            parts.append(obj.patronymic)
        return ' '.join(parts)
    def get_total_medals(self, obj):
        """Считаем количество медалей"""
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
            'total_hours',
            'members_count',
            'team_id',
        ]

    def get_total_hours(self, obj):
        """Складываем часы работы всех стедентов"""
        from django.db.models import Sum

        team = obj.teams_set.first()
        if team:
            result = Student_Activity.objects.filter(
                team=team,
            ).aggregate(total=Sum('hours_weekly'))

            return result['total'] or 0

        return 0

    def get_members_count(self, obj):
        """Считаем количество участников в команде проекта"""

        team = obj.teams_set.first()
        return team.student_teams_set.count() if team else 0

    def get_team_id(self, obj):
        """Получаем ID команды проекта"""

        team = obj.teams_set.first()
        return team.team_id if team else None


class LoginSerializer(serializers.Serializer):
    """Принимаем логин и пароль"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ConsentSerializer(serializers.Serializer):
    """Принимаем решение по согласию"""
    consent = serializers.BooleanField()
    temp_token = serializers.CharField()


class UserInfoSerializer(serializers.ModelSerializer):
    """Отдатет информацию о пользователе"""
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'role'
        ]

    def get_full_name(self, obj):
        parts = [obj.first_name, obj.last_name]
        return ' '.join(filter(None, parts)) or obj.username

    def get_role(self, obj):
        if obj.is_superuser:
            return 'admin'
        if obj.groups.filter(name='manager').exists():
            return 'manager'
        return 'student'


class MeSerializer(serializers.Serializer):
    """Полная информация о текущем пользователе"""

    def to_representation(self, instance):
        # Данные пользователя
        user_data = UserInfoSerializer(instance).data

        # Данные студента
        try:
            student = Students.objects.get(user=instance)
            student_data = StudentShortSerializer(student).data
        except Students.DoesNotExist:
            student_data = None

        # Статус согласия
        try:
            consent_given = instance.userconsent.is_given
        except:
            consent_given = False

        return {
            'user': user_data,
            'student': student_data,
            'consent_given': consent_given
        }