import logging
from typing import List, Optional, Any
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django.core.cache import cache

from LeaderBoard.models import (
    Students, Projects, Teams, Student_Teams, Student_Activity,
    ExternalSource, SyncRun, SyncError, RawApiLog, ProjectCheckpoint
)
from LeaderBoard.integrations.tpu import TPUStudentDTO, TPUApiError
from LeaderBoard.integrations.vitrina import (
    VitrinaProjectDTO, VitrinaActivityDTO, VitrinaApiError
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
    """Синхронизирует проекты из Витрины (финальная версия формата)"""
    context = SyncContext(sync_run)
    
    for dto in projects_dto:
        try:
            if not dto.external_id:
                context.add_error(
                    external_id=None,
                    error_message="Project external_id is empty",
                    payload={'title': dto.title},
                )
                continue
            
            # Идемпотентный upsert по external_id
            project, created = Projects.objects.update_or_create(
                external_id=dto.external_id,
                defaults={
                    'project_name': dto.title,
                    'description': dto.description or '',
                    'project_type': dto.project_type,
                    'status': dto.status,
                    'category': dto.primary_tag or '',
                    'partner': dto.partner_name or '',
                    'is_promoted': dto.is_promoted,
                }
            )
            
            if created:
                context.add_created()
            else:
                context.add_updated()
            
            # Синхронизируем checkpoints
            _sync_project_checkpoints(project, dto.checkpoints)
        
        except Exception as e:
            context.add_error(
                external_id=dto.external_id,
                error_message=str(e),
                payload={'external_id': dto.external_id, 'title': dto.title},
                error_type=type(e).__name__,
            )
    
    context.finalize(received=len(projects_dto))
    
    return {
        'received': len(projects_dto),
        'created': context.created,
        'updated': context.updated,
        'failed': context.failed,
    }


def _sync_project_checkpoints(project, checkpoints_dto) -> None:
    """Синхронизирует контрольные точки проекта"""
    from LeaderBoard.models import ProjectCheckpoint
    
    for cp_dto in checkpoints_dto:
        ProjectCheckpoint.objects.update_or_create(
            project=project,
            title=cp_dto.title,
            defaults={
                'deadline': cp_dto.deadline,
                'is_custom': cp_dto.is_custom,
            }
        )
    
    # Удаляем чекпоинты, которых больше нет в API
    current_titles = {cp.title for cp in checkpoints_dto}
    ProjectCheckpoint.objects.filter(project=project).exclude(
        title__in=current_titles
    ).delete()


# КЕШ И МАППИНГ tpu_user_id → login (через Redis + API ТПУ)

# Sentinel для кеширования None (чтобы не долбить API по несуществующим ID)
_SENTINEL_NONE = '__NONE__'


def _tpu_user_cache_key(tpu_user_id: int) -> str:
    """Формирует ключ кеша для tpu_user_id"""
    from django.conf import settings
    prefix = getattr(settings, 'TPU_USER_CACHE_PREFIX', 'tpu_user_to_login')
    return f'{prefix}:{tpu_user_id}'


def _cache_result(cache_key: str, value: Optional[str], use_cache: bool) -> None:
    """Сохраняет результат в Redis кеш с TTL"""
    if not use_cache:
        return
    
    from django.conf import settings
    ttl = getattr(settings, 'TPU_USER_CACHE_TTL', 60 * 60 * 24)
    
    # Кешируем None через sentinel, чтобы не долбить API на несуществующих tpu_user_id
    if value is None:
        cache.set(cache_key, _SENTINEL_NONE, ttl)
    else:
        cache.set(cache_key, value, ttl)


def map_tpu_user_id_to_login(tpu_user_id: int, use_cache: bool = True) -> Optional[str]:
    """
    Маппит tpu_user_id в login студента через Redis кеш.
    
    Используется для получения login студента по его ID в системе ТПУ.
    Данные берутся из поля role.places в проектах Витрины (участники команды).
    
    Стратегия:
    1. Проверяем Redis кеш (БД 1, TTL 24 часа)
    2. Ищем студента по someone_id в БД (быстрый способ)
    3. Если не найден — запрашиваем профиль из API ТПУ /users/{tpu_user_id}
       и создаём/обновляем студента в БД
    4. Сохраняем результат в кеш
    
    Args:
        tpu_user_id: ID пользователя в системе ТПУ (из role.places)
        use_cache: Использовать Redis кеш

    Returns:
        login студента или None
    """
    if not tpu_user_id:
        return None

    cache_key = _tpu_user_cache_key(tpu_user_id)

    # 1. Проверяем кеш
    if use_cache:
        cached = cache.get(cache_key)
        if cached is not None:
            if cached == _SENTINEL_NONE:
                logger.debug(f"tpu_user_id {tpu_user_id} -> None (from cache)")
                return None
            logger.debug(f"Mapped tpu_user_id {tpu_user_id} -> {cached} (from cache)")
            return cached

    # 2. Быстрый поиск в БД по someone_id
    student = Students.objects.filter(someone_id=str(tpu_user_id)).first()
    if student:
        logger.debug(f"Mapped tpu_user_id {tpu_user_id} -> {student.login} (from DB)")
        _cache_result(cache_key, student.login, use_cache)
        return student.login

    # 3. Запрос к API ТПУ
    logger.info(f"Student with tpu_user_id={tpu_user_id} not in DB, fetching from TPU API")
    from LeaderBoard.integrations.factory import get_tpu_client

    try:
        client = get_tpu_client()
        user_dto = client.get_user_profile(tpu_user_id)
    except Exception as e:
        logger.warning(f"Failed to fetch TPU user profile for tpu_user_id={tpu_user_id}: {e}")
        _cache_result(cache_key, None, use_cache)
        return None

    if not user_dto:
        logger.warning(f"TPU user profile not found for tpu_user_id={tpu_user_id}")
        _cache_result(cache_key, None, use_cache)
        return None

    # 4. Создаём/обновляем студента на основе данных ТПУ
    try:
        student, created = Students.objects.update_or_create(
            login=user_dto.login,
            defaults={
                'someone_id': str(tpu_user_id),
                'first_name': user_dto.first_name or '',
                'last_name': user_dto.last_name or '',
                'patronymic': user_dto.patronym or '',
                'student_group': user_dto.group or '',
                'direction_name': user_dto.school or '',
                'study_year': int(user_dto.course) if user_dto.course and user_dto.course.isdigit() else None,
                'faculty': user_dto.school or '',
            }
        )

        logger.info(
            f"Mapped tpu_user_id {tpu_user_id} -> {student.login} "
            f"({'created' if created else 'updated'})"
        )

        _cache_result(cache_key, student.login, use_cache)
        return student.login

    except Exception as e:
        logger.error(f"Failed to create/update student from TPU user profile: {e}")
        return None


def invalidate_tpu_user_cache(tpu_user_id: int) -> None:
    """Инвалидирует кеш для конкретного tpu_user_id"""
    cache.delete(_tpu_user_cache_key(tpu_user_id))


def clear_tpu_user_cache() -> None:
    """Очищает весь кеш маппинга tpu_user_id → login"""
    from django.conf import settings
    prefix = getattr(settings, 'TPU_USER_CACHE_PREFIX', 'tpu_user_to_login')
    pattern = f'{prefix}:*'
    
    try:
        cache.delete_pattern(pattern)
        logger.info(f"Cleared tpu_user_id cache (pattern: {pattern})")
    except AttributeError:
        # cache.delete_pattern может не поддерживаться некоторыми бэкендами
        logger.warning("cache.delete_pattern not available; cache will expire by TTL")

# Синхронизация участников команд из витрины (через проекты)
@transaction.atomic
def sync_team_members_from_projects(projects_dto: list, sync_run: SyncRun) -> dict:
    """
    Синхронизирует участников команд на основе данных из проектов.
    
    Берёт tpu_user_id ТОЛЬКО из поля role.places (участники команды).
    Поле project.ownerId (владелец проекта/наставник) пока игнорируем.
    """
    context = SyncContext(sync_run)
    total_members = 0
    
    for project_dto in projects_dto:
        try:
            # Находим проект в БД по external_id
            project = Projects.objects.filter(external_id=project_dto.external_id).first()
            if not project:
                logger.warning(f"Project {project_dto.external_id} not found in DB, skipping")
                continue
            
            # Получаем или создаём команду проекта
            team, _ = Teams.objects.get_or_create(
                project=project,
                defaults={
                    'expert_score': '',
                    'period_start': None,
                    'period_end': None,
                }
            )
            
            # Обрабатываем роли — берём только places (участники)
            for role_dto in project_dto.roles:
                for tpu_user_id in role_dto.places:  # ← только участники
                    total_members += 1
                    
                    # Маппим tpu_user_id → login через Redis кеш
                    student_login = map_tpu_user_id_to_login(tpu_user_id)
                    
                    if not student_login:
                        context.add_error(
                            external_id=str(tpu_user_id),
                            error_message=f"Student with tpu_user_id={tpu_user_id} not found",
                            payload={
                                'tpu_user_id': tpu_user_id,
                                'role': role_dto.role_name,
                                'project': project_dto.external_id,
                            },
                        )
                        continue
                    
                    # Находим студента
                    student = Students.objects.filter(login=student_login).first()
                    if not student:
                        context.add_error(
                            external_id=student_login,
                            error_message=f"Student {student_login} not found in DB",
                            payload={'tpu_user_id': tpu_user_id},
                        )
                        continue
                    
                    # Создаём связь студент-команда
                    try:
                        member, created = Student_Teams.objects.update_or_create(
                            student=student,
                            team=team,
                            defaults={
                                'rol': 'Студент',
                                'stack': role_dto.role_name,  # Frontend, Backend, etc.
                            }
                        )
                        
                        if created:
                            context.add_created()
                        else:
                            context.add_updated()
                    
                    except Exception as e:
                        context.add_error(
                            external_id=student_login,
                            error_message=str(e),
                            payload={'tpu_user_id': tpu_user_id, 'team_id': team.team_id},
                            error_type=type(e).__name__,
                        )
        
        except Exception as e:
            context.add_error(
                external_id=project_dto.external_id,
                error_message=str(e),
                payload={'project': project_dto.external_id},
                error_type=type(e).__name__,
            )
    
    context.finalize(received=total_members)
    
    return {
        'received': total_members,
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
    # Очищаем кеш tpu_user_id перед каждой синхронизацией
    clear_tpu_user_cache()
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
    """Полный цикл синхронизации Витрины (с пагинацией и участниками команд)"""
    source = get_or_create_source('VITRINA', 'API Витрины', client.base_url)
    
    results = {
        'projects': None,
        'team_members': None,
        'activities': None,
    }
    
    # 1. Синхронизация проектов (все через пагинацию)
    sync_run_projects = start_sync_run(source, 'sync_vitrina_projects')
    projects = []
    try:
        projects = client.get_all_projects(page_size=20, status=None)
        
        log_raw_response(
            source=source,
            endpoint='/projects',
            sync_run=sync_run_projects,
            status_code=200,
            response_body={'count': len(projects)}
        )
        
        results['projects'] = sync_vitrina_projects(projects, sync_run_projects)
        logger.info(f"Projects sync: {results['projects']}")
        
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
    
    # 2. Синхронизация участников команд (только если проекты загружены)
    if projects:
        sync_run_members = start_sync_run(source, 'sync_team_members')
        try:
            results['team_members'] = sync_team_members_from_projects(projects, sync_run_members)
            logger.info(f"Team members sync: {results['team_members']}")
        except Exception as e:
            sync_run_members.status = 'failed'
            sync_run_members.error_message = str(e)
            sync_run_members.finished_at = timezone.now()
            sync_run_members.save()
            logger.error(f"Team members sync failed: {e}")
    
    # TODO 3. Синхронизация активностей (заглушка)
    sync_run_activities = start_sync_run(source, 'sync_vitrina_activities')
    try:
        activities = client.get_activities()
        log_raw_response(
            source=source,
            endpoint='/activities',
            sync_run=sync_run_activities,
            status_code=200,
            response_body={'count': len(activities)}
        )
        
        if activities:
            results['activities'] = sync_vitrina_activities(activities, sync_run_activities)
        else:
            sync_run_activities.status = 'success'
            sync_run_activities.finished_at = timezone.now()
            sync_run_activities.save()
    except Exception as e:
        sync_run_activities.status = 'failed'
        sync_run_activities.error_message = str(e)
        sync_run_activities.finished_at = timezone.now()
        sync_run_activities.save()
        logger.error(f"Vitrina activities sync failed: {e}")
    
    return results