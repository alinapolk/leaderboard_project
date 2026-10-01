from datetime import datetime
from typing import List, Any, Optional
from decimal import Decimal, InvalidOperation

from .dto import (
    VitrinaActivityDTO,
    VitrinaProjectDTO,
    VitrinaCheckpointDTO,
    VitrinaRoleDTO,
)


def _strip_keys(data: Any) -> Any:
    """
    Рекурсивно убирает пробелы из ключей словаря.
    Нужно, если реальное API возвращает ключи вида "id " вместо "id".
    """
    if isinstance(data, dict):
        return {str(k).strip(): _strip_keys(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_strip_keys(item) for item in data]
    return data


def _get(data: dict, key: str, default=None):
    """Безопасное получение значения с учётом возможных пробелов"""
    if key in data:
        return data[key]
    if f"{key} " in data:
        return data[f"{key} "]
    return default


def _parse_date(value: Any):
    """Парсит дату из разных форматов"""
    if not value:
        return None
    if isinstance(value, str):
        value = value.strip()
        for fmt in ('%Y-%m-%d', '%d.%m.%Y'):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
    return None


def _map_checkpoint(item: dict, is_custom: bool = False) -> Optional[VitrinaCheckpointDTO]:
    """Маппит одну контрольную точку"""
    try:
        title = _get(item, 'title', '')
        deadline = _parse_date(_get(item, 'deadline'))
        if not title or not deadline:
            return None
        return VitrinaCheckpointDTO(
            title=title.strip(),
            deadline=deadline,
            is_custom=is_custom,
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to map checkpoint: {item} — {e}")
        return None


def _map_role(item: dict) -> Optional[VitrinaRoleDTO]:
    """Маппит одну роль в команде"""
    try:
        role_type = _get(item, 'roleType', {}) or {}
        places = _get(item, 'places', []) or []
        
        return VitrinaRoleDTO(
            role_id=str(_get(item, 'roleId', '')).strip(),
            role_name=str(_get(role_type, 'name', '')).strip(),
            places_count=int(_get(item, 'placesCount', 0) or 0),
            min_places_count=int(_get(item, 'minPlacesCount', 0) or 0),
            places=[int(p) for p in places if p is not None],
            applications_count=int(_get(item, 'applicationsCount', 0) or 0),
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to map role: {item} — {e}")
        return None


def map_projects(data: Any) -> List[VitrinaProjectDTO]:
    """
    Преобразует ответ Витрины в список проектов.
    
    Формат ответа:
    {
        "hits": [...],
        "total": 3,
        "offset": 0,
        "limit": 20
    }
    """
    # Если нужно — убираем пробелы из всех ключей
    data = _strip_keys(data)
    
    projects_data = []
    if isinstance(data, dict):
        projects_data = data.get('hits', []) or data.get('projects', [])
    elif isinstance(data, list):
        projects_data = data
    
    result = []
    for item in projects_data:
        try:
            # Метаданные
            meta = _get(item, 'meta', {}) or {}
            partner = _get(item, 'partner', {}) or {}
            primary_tag = _get(item, 'primaryTag', {}) or {}
            tags_raw = _get(item, 'tags', []) or []
            
            # Checkpoints (обычные + кастомные)
            checkpoints_data = _get(item, 'checkpoints', {}) or {}
            checkpoints_list = _get(checkpoints_data, 'checkpoints', []) or []
            custom_checkpoints = _get(item, 'customCheckpoints', []) or []
            
            checkpoints = []
            for cp in checkpoints_list:
                mapped = _map_checkpoint(cp, is_custom=False)
                if mapped:
                    checkpoints.append(mapped)
            for cp in custom_checkpoints:
                mapped = _map_checkpoint(cp, is_custom=True)
                if mapped:
                    checkpoints.append(mapped)
            
            # Roles
            roles_raw = _get(item, 'roles', []) or []
            roles = [r for r in (_map_role(role) for role in roles_raw) if r]
            
            # Repository
            repositories = _get(item, 'repository', []) or []
            repository_url = repositories[0].get('url') if repositories else None
            
            dto = VitrinaProjectDTO(
                external_id=str(_get(item, 'id', '')).strip(),
                project_type=str(_get(item, 'type', '')).strip(),
                status=str(_get(item, 'status', '')).strip(),
                owner_id=_get(item, 'ownerId'),
                title=str(_get(meta, 'title', '')).strip(),
                description=_get(meta, 'description'),
                partner_name=_get(partner, 'name'),
                primary_tag=_get(primary_tag, 'tagName'),
                tags=[_get(t, 'tagName', '') for t in tags_raw if _get(t, 'tagName')],
                is_promoted=bool(_get(item, 'isPromoted', False)),
                checkpoints=checkpoints,
                roles=roles,
                repository_url=repository_url,
            )
            
            if dto.external_id and dto.title:
                result.append(dto)
        
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to map project: {item} — {e}")
    
    return result


def map_activities(data: Any) -> List['VitrinaActivityDTO']:
    """Преобразует ответ в список активностей"""
    from .dto import VitrinaActivityDTO
    
    data = _strip_keys(data)
    
    activities_data = []
    if isinstance(data, dict):
        activities_data = data.get('activities', []) or data.get('hits', [])
    elif isinstance(data, list):
        activities_data = data
    
    result = []
    for item in activities_data:
        try:
            hours = _get(item, 'hours_weekly', 0)
            try:
                hours_decimal = Decimal(str(hours))
            except (InvalidOperation, TypeError):
                hours_decimal = Decimal('0')
            
            weekly_period = _parse_date(_get(item, 'weekly_period'))
            
            if not weekly_period:
                continue
            
            dto = VitrinaActivityDTO(
                student_login=str(_get(item, 'student_login', '')).strip(),
                team_id=str(_get(item, 'team_id', '')).strip(),
                hours_weekly=hours_decimal,
                weekly_period=weekly_period,
            )
            
            if dto.student_login and dto.team_id:
                result.append(dto)
        
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to map activity: {item} — {e}")
    
    return result