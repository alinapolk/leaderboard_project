def calculate_rating_score(study_score, hours):
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
    study = float(study_score or 0)
    hours = float(hours or 0)

    study_norm = study / 5.0
    hours_norm = min(hours / 288.0, 1.0)

    return round(study_norm * 0.5 + hours_norm * 0.5, 6)