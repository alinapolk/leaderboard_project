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


@dataclass
class TPUUserDTO:
    """DTO для пользователя ТПУ (из эндпоинта /users/{targetId})"""
    user_id: int
    email: str
    login: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronym: Optional[str] = None
    course: Optional[str] = None
    group: Optional[str] = None
    school: Optional[str] = None
    telegram: Optional[str] = None
    vk: Optional[str] = None
    element: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: dict) -> Optional['TPUUserDTO']:
        """
        Парсит ответ API ТПУ.

        Пример ответа:
        {
            "userId": 283991,
            "email": "nvs72@tpu.ru",
            "meta": {"firstName": "Никита", "lastName": "Скурков", "patronym": "Вячеславович"},
            "roles": {"Student": {"course": "4", "school": "ИШИТР", "meta": {"group": "8К33"}}},
            "meta": {"messengers": {"telegram": null, "vk": null, "element": "@nvs72"}}
        }
        """
        if not data or not isinstance(data, dict):
            return None

        user_id = data.get('userId')
        email = data.get('email', '')

        if not user_id or not email:
            return None

        # Login = часть email до @
        login = email.split('@')[0] if '@' in email else email

        meta = data.get('meta', {}) or {}
        roles = data.get('roles', {}) or {}
        student_role = roles.get('Student', {}) or {}
        student_meta = student_role.get('meta', {}) or {}
        messengers = meta.get('messengers', {}) or {}

        return cls(
            user_id=user_id,
            email=email,
            login=login,
            first_name=meta.get('firstName'),
            last_name=meta.get('lastName'),
            patronym=meta.get('patronym'),
            course=student_role.get('course'),
            group=student_meta.get('group'),
            school=student_role.get('school'),
            telegram=messengers.get('telegram'),
            vk=messengers.get('vk'),
            element=messengers.get('element'),
        )