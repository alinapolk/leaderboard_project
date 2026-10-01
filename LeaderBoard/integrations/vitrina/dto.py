from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional, List


@dataclass
class VitrinaCheckpointDTO:
    """DTO для контрольной точки (дедлайна)"""
    title: str
    deadline: Optional[date]
    is_custom: bool = False


@dataclass
class VitrinaRoleDTO:
    """DTO для роли в команде"""
    role_id: str
    role_name: str                    # Frontend, Backend, ML-инженер и т.д.
    places_count: int                 # Всего мест
    min_places_count: int             # Минимум мест
    places: List[int] = field(default_factory=list)  # ID занятых мест
    applications_count: int = 0


@dataclass
class VitrinaProjectDTO:
    """DTO для проекта из Витрины"""
    external_id: str                  # id проекта (строка)
    project_type: str                 # Case / Study
    status: str                       # Recruiting и т.д.
    owner_id: Optional[int]           # ID владельца
    title: str
    description: Optional[str]
    partner_name: Optional[str]
    primary_tag: Optional[str]        # FinTech, E-commerce
    tags: List[str] = field(default_factory=list)
    is_promoted: bool = False
    checkpoints: List[VitrinaCheckpointDTO] = field(default_factory=list)
    roles: List[VitrinaRoleDTO] = field(default_factory=list)
    repository_url: Optional[str] = None


@dataclass
class VitrinaActivityDTO:
    """DTO для активности студента (часы)"""
    student_login: str
    team_id: str
    hours_weekly: Decimal
    weekly_period: date