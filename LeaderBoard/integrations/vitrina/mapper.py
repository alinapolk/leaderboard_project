from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Any

from .dto import (
    VitrinaProjectDTO,
    VitrinaTeamDTO,
    VitrinaTeamMemberDTO,
    VitrinaActivityDTO,
)


def _parse_date(value: Any):
    """Парсит дату из разных форматов"""
    if not value:
        return None
    if isinstance(value, str):
        for fmt in ('%Y-%m-%d', '%d.%m.%Y'):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
    return None


def map_projects(data: Any) -> List[VitrinaProjectDTO]:
    """Преобразует ответ в список проектов"""
    projects_data = []
    
    if isinstance(data, dict) and 'projects' in data:
        projects_data = data['projects']
    elif isinstance(data, list):
        projects_data = data
    
    result = []
    for item in projects_data:
        try:
            dto = VitrinaProjectDTO(
                id_project=str(item.get('id_project', '')),
                project_name=str(item.get('project_name', '')),
                description=item.get('description'),
                info_akadem=item.get('info_akadem'),
            )
            result.append(dto)
        except (KeyError, ValueError, TypeError) as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to map project: {item} — {e}")
    
    return result


def map_teams(data: Any) -> List[VitrinaTeamDTO]:
    """Преобразует ответ в список команд"""
    teams_data = data.get('teams', []) if isinstance(data, dict) else data
    
    result = []
    for item in teams_data:
        try:
            dto = VitrinaTeamDTO(
                team_id=str(item.get('team_id', '')),
                project_id=str(item.get('project_id', '')),
                expert_score=item.get('expert_score'),
                period_start=_parse_date(item.get('period_start')),
                period_end=_parse_date(item.get('period_end')),
            )
            result.append(dto)
        except (KeyError, ValueError, TypeError) as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to map team: {item} — {e}")
    
    return result


def map_activities(data: Any) -> List[VitrinaActivityDTO]:
    """Преобразует ответ в список активностей"""
    activities_data = data.get('activities', []) if isinstance(data, dict) else data
    
    result = []
    for item in activities_data:
        try:
            hours = item.get('hours_weekly', 0)
            try:
                hours_decimal = Decimal(str(hours))
            except (InvalidOperation, TypeError):
                hours_decimal = Decimal('0')
            
            dto = VitrinaActivityDTO(
                student_login=str(item.get('student_login', '')),
                team_id=str(item.get('team_id', '')),
                hours_weekly=hours_decimal,
                weekly_period=_parse_date(item.get('weekly_period')),
            )
            if dto.weekly_period:  # Только если дата корректна
                result.append(dto)
        except (KeyError, ValueError, TypeError) as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to map activity: {item} — {e}")
    
    return result