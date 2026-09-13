from django.contrib import admin
from .models import (
    Students, Projects, Teams,
    Student_Teams, Student_Activity, Student_Medals,
    UserConsent
)


# СТУДЕНТЫ
@admin.register(Students)
class StudentsAdmin(admin.ModelAdmin):
    list_display = (
        'login', 'full_name_display', 'student_group',
        'study_year', 'study_score', 'history_work_all',
        'rating_score', 'top_view'
    )
    list_filter = ('faculty', 'student_group', 'study_year', 'top_view')
    search_fields = ('login', 'first_name', 'last_name', 'patronymic')
    ordering = ('-rating_score',)
    readonly_fields = ('rating_score',)

    fieldsets = (
        ('Идентификация', {
            'fields': ('login', 'someone_id', 'user')
        }),
        ('Личные данные', {
            'fields': ('first_name', 'last_name', 'patronymic')
        }),
        ('Учебная информация', {
            'fields': ('student_group', 'direction_name', 'study_year',
                       'faculty', 'study_score', 'debt_count')
        }),
        ('Проектная активность', {
            'fields': ('history_work_all', 'history_work_sem',
                       'history_work_month', 'history_work_week')
        }),
        ('Рейтинг', {
            'fields': ('rating_score', 'top_view')
        }),
    )

    def full_name_display(self, obj):
        parts = [obj.last_name, obj.first_name]
        if obj.patronymic:
            parts.append(obj.patronymic)
        return ' '.join(parts)

    full_name_display.short_description = 'ФИО'


# ПРОЕКТЫ
@admin.register(Projects)
class ProjectsAdmin(admin.ModelAdmin):
    list_display = ('id_project', 'project_name', 'teams_count')
    search_fields = ('project_name',)

    def teams_count(self, obj):
        return obj.teams_set.count()

    teams_count.short_description = 'Команд'


# КОМАНДЫ
@admin.register(Teams)
class TeamsAdmin(admin.ModelAdmin):
    list_display = (
        'team_id', 'project', 'expert_score',
        'period_start', 'period_end', 'members_count'
    )
    list_filter = ('project',)
    search_fields = ('project__project_name',)

    def members_count(self, obj):
        return obj.student_teams_set.count()

    members_count.short_description = 'Участников'


# УЧАСТНИКИ КОМАНД
@admin.register(Student_Teams)
class StudentTeamsAdmin(admin.ModelAdmin):
    list_display = ('team', 'student', 'rol', 'joined_date')
    list_filter = ('rol',)
    search_fields = (
        'student__last_name', 'student__first_name',
        'team__project__project_name'
    )


# АКТИВНОСТЬ
@admin.register(Student_Activity)
class StudentActivityAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'team', 'hours_weekly', 'weekly_period'
    )
    list_filter = ('weekly_period', 'team')
    search_fields = ('student__last_name', 'student__first_name')
    date_hierarchy = 'weekly_period'


# МЕДАЛИ
@admin.register(Student_Medals)
class StudentMedalsAdmin(admin.ModelAdmin):
    list_display = ('student', 'medal_name', 'grade', 'award_date')
    list_filter = ('grade', 'medal_name')
    search_fields = ('student__last_name', 'student__first_name')
    date_hierarchy = 'award_date'


# СОГЛАСИЯ
@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_given', 'ip_address', 'consent_date')
    list_filter = ('is_given',)
    search_fields = ('user__username',)
    readonly_fields = ('ip_address', 'consent_date')