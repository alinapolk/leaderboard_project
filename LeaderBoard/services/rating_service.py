from decimal import Decimal
from django.db import transaction
from django.db.models import QuerySet

from LeaderBoard.models import Students, RatingSnapshot


# Константы
MAX_STUDY_SCORE = Decimal('5.0')
STUDY_WEIGHT = Decimal('0.5')
WORK_WEIGHT = Decimal('0.5')
FORMULA_VERSION = 'v2'

# Нормы часов для разных периодов
# 288 = 36 + 36 + 216 (норма за всё время)
WORK_HOURS_NORMS = {
    'week': Decimal('6.0'),      # ~288 / 48 недель
    'month': Decimal('24.0'),    # ~288 / 12 месяцев
    'sem': Decimal('144.0'),     # ~288 / 2 семестра
    'all': Decimal('288.0'),     # Полная норма
}

# Соответствие периода -> поле часов в модели
PERIOD_HOURS_FIELD = {
    'week': 'history_work_week',
    'month': 'history_work_month',
    'sem': 'history_work_sem',
    'all': 'history_work_all',
}

# Соответствие периода -> поле рейтинга в модели
PERIOD_RATING_FIELD = {
    'week': 'rating_score_week',
    'month': 'rating_score_month',
    'sem': 'rating_score_sem',
    'all': 'rating_score',
}

# Все доступные периоды
AVAILABLE_PERIODS = ['week', 'month', 'sem', 'all']


# Расчёт рейтинга
def calculate_rating_score(study_score, hours, period: str = 'all') -> Decimal:
    """
    Пересчитывает rating_score за указанный период.

    Формула:
        rating_score = (study_score / 5.0) * 0.5 + min(hours / norm, 1.0) * 0.5

    Где:
        study_score — оценка из ТПУ (0–5)
        hours — часы за указанный период
        norm — норма часов для периода (6 / 24 / 144 / 288)

    Результат: от 0.0 до 1.0
    """
    study = Decimal(str(study_score or 0))
    hours = Decimal(str(hours or 0))
    norm = WORK_HOURS_NORMS.get(period, WORK_HOURS_NORMS['all'])

    study_norm = study / MAX_STUDY_SCORE
    hours_norm = min(hours / norm, Decimal('1.0'))

    return (study_norm * STUDY_WEIGHT + hours_norm * WORK_WEIGHT).quantize(Decimal('0.000001'))


def calculate_rating_components(study_score, hours, period: str = 'all') -> dict:
    """Возвращает компоненты рейтинга отдельно"""
    study = Decimal(str(study_score or 0))
    hours = Decimal(str(hours or 0))
    norm = WORK_HOURS_NORMS.get(period, WORK_HOURS_NORMS['all'])

    study_component = (study / MAX_STUDY_SCORE * STUDY_WEIGHT).quantize(Decimal('0.000001'))
    work_component = (min(hours / norm, Decimal('1.0')) * WORK_WEIGHT).quantize(Decimal('0.000001'))

    return {
        'study_component': study_component,
        'work_component': work_component,
        'total': study_component + work_component,
        'period': period,
        'hours_norm': norm,
    }


def calculate_all_periods_rating(student) -> dict:
    """
    Пересчитывает рейтинги студента за все периоды.
    
    Возвращает словарь {период: рейтинг}.
    """
    results = {}
    for period in AVAILABLE_PERIODS:
        hours_field = PERIOD_HOURS_FIELD[period]
        hours = getattr(student, hours_field, 0)
        results[period] = calculate_rating_score(student.study_score, hours, period)
    return results



# Пересчёт для одного студента
@transaction.atomic
def recalculate_student_rating(
    student: Students,
    reason: str = 'manual_recalc',
    create_snapshot: bool = True
) -> dict:
    """
    Пересчитывает рейтинги студента за все периоды.
    
    Возвращает словарь с новыми рейтингами.
    """
    ratings = calculate_all_periods_rating(student)

    # Обновляем все поля рейтинга
    student.rating_score = ratings['all']
    student.rating_score_week = ratings['week']
    student.rating_score_month = ratings['month']
    student.rating_score_sem = ratings['sem']
    
    student.save(update_fields=[
        'rating_score',
        'rating_score_week',
        'rating_score_month',
        'rating_score_sem',
    ])

    # Создаём снимок истории (для основного рейтинга)
    if create_snapshot:
        components = calculate_rating_components(
            student.study_score,
            student.history_work_all,
            period='all'
        )
        RatingSnapshot.objects.create(
            student=student,
            score=ratings['all'],
            study_score=student.study_score,
            history_work_all=student.history_work_all,
            study_component=components['study_component'],
            work_component=components['work_component'],
            formula_version=FORMULA_VERSION,
            reason=reason
        )

    return ratings


# Пересчёт всех студентов
@transaction.atomic
def recalculate_all_ratings(
    reason: str = 'weekly_recalc',
    create_snapshots: bool = False
) -> dict:
    """
    Пересчитывает рейтинги за ве периоды для всех студентов.
    Использует bulk_update для производительности.
    """
    students = list(Students.objects.all())
    total = len(students)
    updated = 0
    students_to_update = []

    rating_fields = [
        'rating_score',
        'rating_score_week',
        'rating_score_month',
        'rating_score_sem',
    ]

    for student in students:
        ratings = calculate_all_periods_rating(student)

        # Проверяем, изменился ли хотя бы один рейтинг
        changed = False
        for period in AVAILABLE_PERIODS:
            field = PERIOD_RATING_FIELD[period]
            current = float(getattr(student, field) or 0)
            new = float(ratings[period])
            if abs(current - new) > 0.000001:
                changed = True
                break

        if changed:
            student.rating_score = ratings['all']
            student.rating_score_week = ratings['week']
            student.rating_score_month = ratings['month']
            student.rating_score_sem = ratings['sem']
            students_to_update.append(student)
            updated += 1

    # Массовое обновление
    if students_to_update:
        Students.objects.bulk_update(
            students_to_update,
            rating_fields,
            batch_size=500
        )

    # Снимки истории (только для основного рейтинга)
    if create_snapshots and students_to_update:
        snapshots = []
        for student in students_to_update:
            components = calculate_rating_components(
                student.study_score,
                student.history_work_all,
                period='all'
            )
            snapshots.append(RatingSnapshot(
                student=student,
                score=student.rating_score,
                study_score=student.study_score,
                history_work_all=student.history_work_all,
                study_component=components['study_component'],
                work_component=components['work_component'],
                formula_version=FORMULA_VERSION,
                reason=reason
            ))
        RatingSnapshot.objects.bulk_create(snapshots, batch_size=500)

    return {
        'total': total,
        'updated': updated,
        'message': f'Обновлено {updated} из {total} студентов'
    }


def get_student_rating_history(student_login: str, limit: int = 10) -> QuerySet:
    """Возвращает историю рейтинга студента"""
    return RatingSnapshot.objects.filter(
        student_id=student_login
    ).order_by('-created_at')[:limit]