from decimal import Decimal
from django.db import transaction
from django.db.models import QuerySet

from LeaderBoard.models import Students, RatingSnapshot


# Константы формулы
MAX_STUDY_SCORE = Decimal('5.0')
STUDY_WEIGHT = Decimal('0.5')
WORK_WEIGHT = Decimal('0.5')
WORK_HOURS_NORM = Decimal('288.0')
FORMULA_VERSION = 'v1'


def calculate_rating_score(study_score, hours) -> Decimal:
    """
    Пересчитывает rating_score перед каждым сохранением.

    Формула:
        rating_score = (study_score / 5.0) * 0.5 + min(hours / 288.0, 1.0) * 0.5

    Где:
        study_score — оценка из ТПУ (0–5)
        hours — суммарные часы (history_work_all)
        288 — норма часов (36 + 36 + 216)
        0.5 — вес каждой части

    Результат: от 0.0 до 1.0
    """
    study = Decimal(str(study_score or 0))
    hours = Decimal(str(hours or 0))

    study_norm = study / MAX_STUDY_SCORE
    hours_norm = min(hours / WORK_HOURS_NORM, Decimal('1.0'))

    return (study_norm * STUDY_WEIGHT + hours_norm * WORK_WEIGHT).quantize(Decimal('0.000001'))


def calculate_rating_components(study_score, hours) -> dict:
    """
    Возвращает компоненты рейтинга отдельно.
    
    Полезно для объяснения, из чего складывается рейтинг.
    """
    study = Decimal(str(study_score or 0))
    hours = Decimal(str(hours or 0))

    study_component = (study / MAX_STUDY_SCORE * STUDY_WEIGHT).quantize(Decimal('0.000001'))
    work_component = (min(hours / WORK_HOURS_NORM, Decimal('1.0')) * WORK_WEIGHT).quantize(Decimal('0.000001'))

    return {
        'study_component': study_component,
        'work_component': work_component,
        'total': study_component + work_component,
    }


@transaction.atomic
def recalculate_student_rating(student: Students, reason: str = 'manual_recalc', create_snapshot: bool = True) -> Decimal:
    """
    Пересчитывает рейтинг для одного студента.
    
    Аргументы:
        student: Объект студента
        reason: Причина пересчёта
        create_snapshot: Создавать ли снимок истории
    
    Возвращает:
        Новый рейтинг
    """
    new_rating = calculate_rating_score(student.study_score, student.history_work_all)
    
    # Обновляем рейтинг студента
    student.rating_score = new_rating
    student.save(update_fields=['rating_score'])
    
    # Создаём снимок истории
    if create_snapshot:
        components = calculate_rating_components(student.study_score, student.history_work_all)
        RatingSnapshot.objects.create(
            student=student,
            score=new_rating,
            study_score=student.study_score,
            history_work_all=student.history_work_all,
            study_component=components['study_component'],
            work_component=components['work_component'],
            formula_version=FORMULA_VERSION,
            reason=reason
        )
    
    return new_rating


@transaction.atomic
def recalculate_all_ratings(reason: str = 'weekly_recalc', create_snapshots: bool = False) -> dict:
    """
    Пересчитывает рейтинг для ВСЕХ студентов.
    
    Использует bulk_update для производительности.
    
    Аргументы:
        reason: Причина пересчёта
        create_snapshots: Создавать ли снимки истории для всех
    
    Возвращает:
        Словарь с результатами
    """
    students = list(Students.objects.all())
    total = len(students)
    updated = 0
    
    students_to_update = []
    
    for student in students:
        new_rating = calculate_rating_score(student.study_score, student.history_work_all)
        current = float(student.rating_score or 0)
        
        if abs(current - float(new_rating)) > 0.000001:
            student.rating_score = new_rating
            students_to_update.append(student)
            updated += 1
    
    # Массовое обновление вместо цикла с save()
    if students_to_update:
        Students.objects.bulk_update(students_to_update, ['rating_score'], batch_size=500)
    
    # Создаём снимки только если запрошено (для экономии места)
    if create_snapshots and students_to_update:
        snapshots = []
        for student in students_to_update:
            components = calculate_rating_components(student.study_score, student.history_work_all)
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