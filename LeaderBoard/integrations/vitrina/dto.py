from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional, List


@dataclass
class VitrinaProjectDTO:
    """DTO для проекта из Витрины"""
    id_project: str
    project_name: str
    description: Optional[str]
    info_akadem: Optional[str]


@dataclass
class VitrinaTeamDTO:
    """DTO для команды из Витрины"""
    team_id: str
    project_id: str
    expert_score: Optional[str]
    period_start: Optional[date]
    period_end: Optional[date]


@dataclass
class VitrinaTeamMemberDTO:
    """DTO для участника команды"""
    student_login: str
    team_id: str
    role: str
    joined_date: Optional[str]


@dataclass
class VitrinaActivityDTO:
    """DTO для активности студента"""
    student_login: str
    team_id: str
    hours_weekly: Decimal
    weekly_period: date