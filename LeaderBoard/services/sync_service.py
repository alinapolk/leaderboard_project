import logging
from typing import List, Optional, Any
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from LeaderBoard.models import (
    Students, Projects, Teams, Student_Teams, Student_Activity,
    ExternalSource, SyncRun, SyncError, RawApiLog
)
from LeaderBoard.integrations.tpu import TPUStudentDTO, TPUApiError
from LeaderBoard.integrations.vitrina import (
    VitrinaProjectDTO, VitrinaTeamDTO, VitrinaActivityDTO, VitrinaApiError, VitrinaTeamMemberDTO
)


logger = logging.getLogger(__name__)


class SyncContext:
    """Контекст выполнения синхронизации — аккумулирует счётчики и ошибки."""
    
    def __init__(self, sync_run: SyncRun):
        self.sync_run = sync_run
        self.created = 0
        self.updated = 0
        self.skipped = 0
        self.failed = 0
        self.errors: List[dict] = []
    
    def add_created(self):
        self.created += 1
    
    def add_updated(self):
        self.updated += 1
    
    def add_skipped(self):
        self.skipped += 1
    
    def add_error(self, external_id: str, error_message: str, payload: Any = None, error_type: str = None):
        self.failed += 1
        self.errors.append({
            'external_id': external_id,
            'error_message': error_message,
            'payload': payload,
            'error_type': error_type,
        })
    
    def finalize(self, received: int, error_message: str = None):
        """Завершает синхронизацию, сохраняет счётчики и ошибки."""
        self.sync_run.records_received = received
        self.sync_run.records_created = self.created
        self.sync_run.records_updated = self.updated
        self.sync_run.records_skipped = self.skipped
        self.sync_run.records_failed = self.failed
        self.sync_run.finished_at = timezone.now()
        
        if error_message:
            self.sync_run.error_message = error_message
            self.sync_run.status = 'failed'
        elif self.failed > 0 and (self.created + self.updated) == 0:
            self.sync_run.status = 'failed'
        elif self.failed > 0:
            self.sync_run.status = 'partial_success'
        else:
            self.sync_run.status = 'success'
        
        self.sync_run.save()
        
        # Сохраняем ошибки в базу
        if self.errors:
            SyncError.objects.bulk_create([
                SyncError(
                    sync_run=self.sync_run,
                    external_id=err.get('external_id'),
                    error_message=err['error_message'],
                    payload=err.get('payload'),
                    error_type=err.get('error_type'),
                )
                for err in self.errors
            ], batch_size=500)


def get_or_create_source(code: str, name: str = None, base_url: str = None) -> ExternalSource:
    """Получает или создаёт внешний источник"""
    source, _ = ExternalSource.objects.get_or_create(
        code=code,
        defaults={
            'name': name or code,
            'base_url': base_url,
        }
    )
    return source


def start_sync_run(source: ExternalSource, task_name: str) -> SyncRun:
    """Создаёт новую запись о запуске синхронизации"""
    return SyncRun.objects.create(
        source=source,
        task_name=task_name,
        status='running'
    )


def log_raw_response(
    source: ExternalSource,
    endpoint: str,
    sync_run: Optional[SyncRun] = None,
    status_code: int = 200,
    response_body: Any = None,
    error_message: str = None,
):
    """Сохраняет сырой ответ API"""
    RawApiLog.objects.create(
        source=source,
        sync_run=sync_run,
        endpoint=endpoint,
        status_code=status_code,
        response_body=response_body,
        error_message=error_message,
    )


# Синхронизация студентов из ТПУ
@transaction.atomic
def sync_tpu_students(students_dto: List[TPUStudentDTO], sync_run: SyncRun) -> dict:
    """
    Синхронизирует студентов из API ТПУ.
    
    Использует идемпотентный update_or_create по полю login.
    """
    context = SyncContext(sync_run)
    
    for dto in students_dto:
        try:
            if not dto.login:
                context.add_error(
                    external_id=None,
                    error_message="Student login is empty",
                    payload={'someone_id': dto.someone_id},
                )
                continue
            
            student, created = Students.objects.update_or_create(
                login=dto.login,
                defaults={
                    'someone_id': dto.someone_id,
                    'first_name': dto.first_name,
                    'last_name': dto.last_name,
                    'patronymic': dto.patronymic or None,
                    'student_group': dto.student_group,
                    'direction_name': dto.direction_name,
                    'study_year': dto.study_year,
                    'faculty': dto.faculty,
                    'study_score': Decimal(str(dto.study_score)) if dto.study_score is not None else None,
                    'debt_count': dto.debt_count,
                }
            )
            
            if created:
                context.add_created()
            else:
                context.add_updated()
        
        except Exception as e:
            context.add_error(
                external_id=dto.login,
                error_message=str(e),
                payload={
                    'login': dto.login,
                    'someone_id': dto.someone_id,
                },
                error_type=type(e).__name__,
            )
            logger.error(f"Error syncing student {dto.login}: {e}")
    
    context.finalize(received=len(students_dto))
    
    return {
        'received': len(students_dto),
        'created': context.created,
        'updated': context.updated,
        'skipped': context.skipped,
        'failed': context.failed,
    }


# Синхронизация проектов из Витрины
@transaction.atomic
def sync_vitrina_projects(projects_dto: List[VitrinaProjectDTO], sync_run: SyncRun) -> dict:
    """Синхронизирует проекты из API Витрины"""
    context = SyncContext(sync_run)
    
    for dto in projects_dto:
        try:
            if not dto.id_project:
                context.add_error(
                    external_id=None,
                    error_message="Project id is empty",
                    payload={'project_name': dto.project_name},
                )
                continue
            
            # Пробуем найти проект по внешнему ID
            # В текущей модели id_project — это AutoField, поэтому для идемпотентности нужен либо внешний ключ, либо переделать модель.
            # Пока используем project_name как fallback
            
            project, created = Projects.objects.update_or_create(
                # TODO: заменить на внешний ID после рефакторинга модели
                project_name=dto.project_name,  
                defaults={
                    'description': dto.description or '',
                    'info_akadem': dto.info_akadem or '',
                }
            )
            
            if created:
                context.add_created()
            else:
                context.add_updated()
        
        except Exception as e:
            context.add_error(
                external_id=dto.id_project,
                error_message=str(e),
                payload={'id_project': dto.id_project, 'project_name': dto.project_name},
                error_type=type(e).__name__,
            )
    
    context.finalize(received=len(projects_dto))
    
    return {
        'received': len(projects_dto),
        'created': context.created,
        'updated': context.updated,
        'failed': context.failed,
    }


# Синхроназция команд из Витрины
@transaction.atomic
def sync_vitrina_teams(teams_dto: List[VitrinaTeamDTO], sync_run: SyncRun) -> dict:
    """Синхронизирует команды из API Витрины"""
    context = SyncContext(sync_run)
    
    for dto in teams_dto:
        try:
            if not dto.team_id or not dto.project_id:
                context.add_error(
                    external_id=dto.team_id,
                    error_message="Team ID or Project ID is empty",
                    payload={'team_id': dto.team_id, 'project_id': dto.project_id},
                )
                continue
            
            # Находим проект по внешнему ID (используем project_name как временный ключ)
            # В идеале нужно хранить внешний ID проекта в модели
            project = Projects.objects.filter(id_project=dto.project_id).first()
            
            if not project:
                context.add_error(
                    external_id=dto.team_id,
                    error_message=f"Project with id_project={dto.project_id} not found",
                    payload={'team_id': dto.team_id, 'project_id': dto.project_id},
                )
                continue
            
            # Создаём команду (если ещё не существует)
            # Используем внешний ID через поиск — нужна доработка модели
            # Пока используем простой подход
            team, created = Teams.objects.get_or_create(
                project=project,
                period_start=dto.period_start,
                defaults={
                    'expert_score': dto.expert_score or '',
                    'period_end': dto.period_end,
                }
            )
            
            if created:
                context.add_created()
            else:
                context.add_skipped()
        
        except Exception as e:
            context.add_error(
                external_id=dto.team_id,
                error_message=str(e),
                payload={'team_id': dto.team_id},
                error_type=type(e).__name__,
            )
    
    context.finalize(received=len(teams_dto))
    
    return {
        'received': len(teams_dto),
        'created': context.created,
        'updated': context.updated,
        'failed': context.failed,
    }


# Синхронизация участников команд из Витрины
@transaction.atomic
def sync_team_members(members_dto: List[VitrinaTeamMemberDTO], sync_run: SyncRun) -> dict:
    """Синхронизирует участников команд из API Витрины"""
    context = SyncContext(sync_run)
    
    for dto in members_dto:
        try:
            if not dto.student_login or not dto.team_id:
                context.add_error(
                    external_id=dto.student_login,
                    error_message="Student login or team_id is missing",
                    payload={
                        'student_login': dto.student_login,
                        'team_id': dto.team_id,
                    },
                )
                continue
            
            # Находим студента
            student = Students.objects.filter(login=dto.student_login).first()
            if not student:
                context.add_error(
                    external_id=dto.student_login,
                    error_message=f"Student with login={dto.student_login} not found",
                    payload={'student_login': dto.student_login},
                )
                continue
            
            # Находим команду
            team = Teams.objects.filter(team_id=dto.team_id).first()
            if not team:
                context.add_error(
                    external_id=dto.student_login,
                    error_message=f"Team with team_id={dto.team_id} not found",
                    payload={'student_login': dto.student_login, 'team_id': dto.team_id},
                )
                continue
            
            # Создаём связь студент-команда (уникальность: team + student)
            member, created = Student_Teams.objects.update_or_create(
                student=student,
                team=team,
                defaults={
                    'rol': dto.role,
                }
            )
            
            if created:
                context.add_created()
            else:
                context.add_updated()
        
        except Exception as e:
            context.add_error(
                external_id=dto.student_login,
                error_message=str(e),
                payload={
                    'student_login': dto.student_login,
                    'team_id': dto.team_id,
                },
                error_type=type(e).__name__,
            )
    
    context.finalize(received=len(members_dto))
    
    return {
        'received': len(members_dto),
        'created': context.created,
        'updated': context.updated,
        'failed': context.failed,
    }


# Синхронизация активности из Витрины
@transaction.atomic
def sync_vitrina_activities(activities_dto: List[VitrinaActivityDTO], sync_run: SyncRun) -> dict:
    """Синхронизирует активность (часы) из API Витрины"""
    context = SyncContext(sync_run)
    
    for dto in activities_dto:
        try:
            if not dto.student_login or not dto.weekly_period:
                context.add_error(
                    external_id=dto.student_login,
                    error_message="Student login or weekly_period is missing",
                    payload={
                        'student_login': dto.student_login,
                        'team_id': dto.team_id,
                        'weekly_period': str(dto.weekly_period) if dto.weekly_period else None,
                    },
                )
                continue
            
            # Находим студента
            student = Students.objects.filter(login=dto.student_login).first()
            if not student:
                context.add_error(
                    external_id=dto.student_login,
                    error_message=f"Student with login={dto.student_login} not found",
                    payload={'student_login': dto.student_login},
                )
                continue
            
            # Находим команду (упрощённый поиск — в реальности нужен внешний ID команды)
            team = Teams.objects.filter(team_id=dto.team_id).first()
            if not team:
                # Пробуем создать заглушку команды или пропускаем
                context.add_error(
                    external_id=dto.student_login,
                    error_message=f"Team with team_id={dto.team_id} not found",
                    payload={'student_login': dto.student_login, 'team_id': dto.team_id},
                )
                continue
            
            # Создаём или обновляем активность (уникальность: student + team + weekly_period)
            activity, created = Student_Activity.objects.update_or_create(
                student=student,
                team=team,
                weekly_period=dto.weekly_period,
                defaults={
                    'hours_weekly': dto.hours_weekly,
                }
            )
            
            if created:
                context.add_created()
            else:
                context.add_updated()
        
        except Exception as e:
            context.add_error(
                external_id=dto.student_login,
                error_message=str(e),
                payload={
                    'student_login': dto.student_login,
                    'team_id': dto.team_id,
                },
                error_type=type(e).__name__,
            )
    
    context.finalize(received=len(activities_dto))
    
    return {
        'received': len(activities_dto),
        'created': context.created,
        'updated': context.updated,
        'failed': context.failed,
    }


# Высокоуровневые функции
def run_full_tpu_sync(client) -> dict:
    """
    Полный цикл синхронизации ТПУ:
    1. Получить данные через клиент
    2. Сохранить сырой ответ
    3. Синхронизировать студентов
    """
    source = get_or_create_source('TPU', 'API ТПУ', client.base_url)
    sync_run = start_sync_run(source, 'sync_tpu_students')
    
    try:
        # Получаем данные
        students = client.get_students()
        
        # Логируем сырой ответ (для режима моков — это сами DTO)
        log_raw_response(
            source=source,
            endpoint='/students',
            sync_run=sync_run,
            status_code=200,
            response_body={
                'students_count': len(students),
                'sample': [
                    {'login': s.login, 'first_name': s.first_name, 'last_name': s.last_name}
                    for s in students[:3]
                ] if students else [],
            }
        )
        
        # Синхронизируем
        result = sync_tpu_students(students, sync_run)
        
        logger.info(f"TPU sync completed: {result}")
        return result
    
    except TPUApiError as e:
        sync_run.status = 'failed'
        sync_run.error_message = str(e)
        sync_run.finished_at = timezone.now()
        sync_run.save()
        
        log_raw_response(
            source=source,
            endpoint='/students',
            sync_run=sync_run,
            error_message=str(e),
        )
        
        logger.error(f"TPU sync failed: {e}")
        raise
    
    except Exception as e:
        sync_run.status = 'failed'
        sync_run.error_message = str(e)
        sync_run.finished_at = timezone.now()
        sync_run.save()
        logger.error(f"TPU sync unexpected error: {e}")
        raise


def run_full_vitrina_sync(client) -> dict:
    """Полный цикл синхронизации Витрины"""
    source = get_or_create_source('VITRINA', 'API Витрины', client.base_url)
    
    results = {
        'projects': None,
        'teams': None,
        'members': None,
        'activities': None,
    }
    
    # 1. Синхронизация проектов
    sync_run_projects = start_sync_run(source, 'sync_vitrina_projects')
    try:
        projects = client.get_projects()
        log_raw_response(
            source=source, endpoint='/projects', sync_run=sync_run_projects,
            status_code=200, response_body={'count': len(projects)}
        )
        results['projects'] = sync_vitrina_projects(projects, sync_run_projects)
    except VitrinaApiError as e:
        sync_run_projects.status = 'failed'
        sync_run_projects.error_message = str(e)
        sync_run_projects.finished_at = timezone.now()
        sync_run_projects.save()
        logger.error(f"Vitrina projects sync failed: {e}")
    except Exception as e:
        sync_run_projects.status = 'failed'
        sync_run_projects.error_message = str(e)
        sync_run_projects.finished_at = timezone.now()
        sync_run_projects.save()
        logger.error(f"Vitrina projects sync unexpected error: {e}")
    
    # 2. Синхронизация команд
    sync_run_teams = start_sync_run(source, 'sync_vitrina_teams')
    try:
        teams = client.get_teams()
        log_raw_response(
            source=source, endpoint='/teams', sync_run=sync_run_teams,
            status_code=200, response_body={'count': len(teams)}
        )
        results['teams'] = sync_vitrina_teams(teams, sync_run_teams)
    except VitrinaApiError as e:
        sync_run_teams.status = 'failed'
        sync_run_teams.error_message = str(e)
        sync_run_teams.finished_at = timezone.now()
        sync_run_teams.save()
        logger.error(f"Vitrina teams sync failed: {e}")
    except Exception as e:
        sync_run_teams.status = 'failed'
        sync_run_teams.error_message = str(e)
        sync_run_teams.finished_at = timezone.now()
        sync_run_teams.save()
        logger.error(f"Vitrina teams sync unexpected error: {e}")
    
    # 3. Синхронизация участников команд
    sync_run_members = start_sync_run(source, 'sync_team_members')
    try:
        # Получаем всех участников всех команд
        all_members = []
        for team in Teams.objects.all():
            try:
                members = client.get_team_members(str(team.team_id))
                all_members.extend(members)
            except VitrinaApiError:
                pass  # Пропускаем ошибки отдельных команд
        
        log_raw_response(
            source=source, endpoint='/teams/{id}/members', sync_run=sync_run_members,
            status_code=200, response_body={'count': len(all_members)}
        )
        results['members'] = sync_team_members(all_members, sync_run_members)
    except Exception as e:
        sync_run_members.status = 'failed'
        sync_run_members.error_message = str(e)
        sync_run_members.finished_at = timezone.now()
        sync_run_members.save()
        logger.error(f"Vitrina team members sync failed: {e}")
    
    # 4. Синхронизация активностей
    sync_run_activities = start_sync_run(source, 'sync_vitrina_activities')
    try:
        activities = client.get_activities()
        log_raw_response(
            source=source, endpoint='/activities', sync_run=sync_run_activities,
            status_code=200, response_body={'count': len(activities)}
        )
        results['activities'] = sync_vitrina_activities(activities, sync_run_activities)
    except VitrinaApiError as e:
        sync_run_activities.status = 'failed'
        sync_run_activities.error_message = str(e)
        sync_run_activities.finished_at = timezone.now()
        sync_run_activities.save()
        logger.error(f"Vitrina activities sync failed: {e}")
    except Exception as e:
        sync_run_activities.status = 'failed'
        sync_run_activities.error_message = str(e)
        sync_run_activities.finished_at = timezone.now()
        sync_run_activities.save()
        logger.error(f"Vitrina activities sync unexpected error: {e}")
    
    return results