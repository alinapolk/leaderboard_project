from dataclasses import dataclass
from typing import Optional


@dataclass
class TPUStudentDTO:
    """
    DTO для студента из API ТПУ.
    
    Представляет данные студента в том виде, как они приходят из внешнего API.
    """
    login: str
    someone_id: str
    first_name: str
    last_name: str
    patronymic: Optional[str]
    student_group: str
    direction_name: str
    study_year: Optional[int]
    faculty: str
    study_score: Optional[float]
    debt_count: Optional[int]