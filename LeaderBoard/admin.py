from django.contrib import admin
from .models import (
    Students, Projects, Teams,
    Student_Teams, Student_Activity, Student_Medals,
    UserConsent, RatingSnapshot, ExternalSource, SyncRun, SyncError, RawApiLog
)


# СТУДЕНТЫ
@admin.register(Students)
class StudentsAdmin(admin.ModelAdmin):
    list_display = (
        'login', 'full_name_display', 'student_group',
        'study_year', 'study_score', 'history_work_all',
        'rating_score', 'rating_score_week', 'rating_score_month',
        'rating_score_sem', 'top_view'
    )
    list_filter = ('faculty', 'student_group', 'study_year', 'top_view')
    search_fields = ('login', 'first_name', 'last_name', 'patronymic')
    ordering = ('-rating_score',)
    readonly_fields = (
        'rating_score', 'rating_score_week', 
        'rating_score_month', 'rating_score_sem'
    )

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
            'fields': (
                'rating_score', 'rating_score_week',
                'rating_score_month', 'rating_score_sem', 'top_view'
            )
        }),
    )

    def full_name_display(self, obj):
        parts = [obj.last_name, obj.first_name]
        if obj.patronymic:
            parts.append(obj.patronymic)
        return ' '.join(parts)

    full_name_display.short_description = 'ФИО'


# ИСТОРИЯ РЕЙТИНГА
@admin.register(RatingSnapshot)
class RatingSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'score', 'study_score', 'history_work_all',
        'formula_version', 'reason', 'created_at'
    )
    list_filter = ('reason', 'formula_version', 'created_at')
    search_fields = ('student__login', 'student__first_name', 'student__last_name')
    readonly_fields = (
        'student', 'score', 'study_score', 'history_work_all',
        'study_component', 'work_component', 'formula_version',
        'reason', 'created_at'
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('Студент', {
            'fields': ('student',)
        }),
        ('Рейтинг', {
            'fields': (
                'score', 'study_score', 'history_work_all',
                'study_component', 'work_component'
            )
        }),
        ('Метаданные', {
            'fields': ('formula_version', 'reason', 'created_at')
        }),
    )


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


# 
@admin.register(ExternalSource)
class ExternalSourceAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'base_url', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')


@admin.register(SyncRun)
class SyncRunAdmin(admin.ModelAdmin):
    list_display = (
        'source', 'task_name', 'status', 'started_at', 'finished_at',
        'records_received', 'records_created', 'records_updated', 'records_failed', 'duration_seconds'
    )
    list_filter = ('source', 'status', 'started_at')
    search_fields = ('task_name', 'error_message')
    readonly_fields = (
        'source', 'task_name', 'status', 'started_at', 'finished_at',
        'records_received', 'records_created', 'records_updated',
        'records_skipped', 'records_failed', 'error_message', 'duration_seconds'
    )
    date_hierarchy = 'started_at'
    
    def duration_seconds(self, obj):
        return f"{obj.duration_seconds:.1f}s" if obj.duration_seconds else "-"
    duration_seconds.short_description = 'Длительность'


@admin.register(SyncError)
class SyncErrorAdmin(admin.ModelAdmin):
    list_display = ('sync_run', 'external_id', 'error_type', 'created_at')
    list_filter = ('sync_run__source', 'error_type', 'created_at')
    search_fields = ('external_id', 'error_message')
    readonly_fields = ('sync_run', 'external_id', 'error_message', 'error_type', 'payload', 'created_at')
    date_hierarchy = 'created_at'


@admin.register(RawApiLog)
class RawApiLogAdmin(admin.ModelAdmin):
    list_display = ('source', 'endpoint', 'status_code', 'created_at')
    list_filter = ('source', 'status_code', 'created_at')
    search_fields = ('endpoint', 'error_message')
    readonly_fields = (
        'source', 'sync_run', 'endpoint', 'request_params',
        'request_body', 'status_code', 'response_body', 'error_message', 'created_at'
    )
    date_hierarchy = 'created_at'