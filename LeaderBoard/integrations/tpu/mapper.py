from typing import Dict, Any, List
from .dto import TPUStudentDTO


def map_tpu_response_to_students(data: Any) -> List[TPUStudentDTO]:
    """
    Преобразует ответ API ТПУ в список DTO студентов.
    
    Структура ответа ТПУ (ожидаемая):
    {
        "students": [
            {
                "login": "ivanov.ii",
                "someone_id": "12345",
                "first_name": "Иван",
                "last_name": "Иванов",
                "patronymic": "Иванович",
                "student_group": "1234",
                "direction_name": "Информатика",
                "study_year": 2,
                "faculty": "ИШИТР",
                "study_score": 4.5,
                "debt_count": 0
            }
        ]
    }
    """
    students_data = []
    
    if isinstance(data, dict) and 'students' in data:
        students_data = data['students']
    elif isinstance(data, list):
        students_data = data
    
    result = []
    for item in students_data:
        try:
            dto = TPUStudentDTO(
                login=str(item.get('login', '')),
                someone_id=str(item.get('someone_id', '')),
                first_name=str(item.get('first_name', '')),
                last_name=str(item.get('last_name', '')),
                patronymic=item.get('patronymic'),
                student_group=str(item.get('student_group', '')),
                direction_name=str(item.get('direction_name', '')),
                study_year=item.get('study_year'),
                faculty=str(item.get('faculty', '')),
                study_score=float(item['study_score']) if item.get('study_score') is not None else None,
                debt_count=int(item['debt_count']) if item.get('debt_count') is not None else None,
            )
            result.append(dto)
        except (KeyError, ValueError, TypeError) as e:
            # Логируем ошибку, но продолжаем обрабатывать остальных
            import logging
            logging.getLogger(__name__).warning(
                f"Failed to map TPU student: {item} — {e}"
            )
    
    return result