import logging
from pathlib import Path
from typing import List, Optional

from ..base_client import BaseApiClient
from .dto import VitrinaProjectDTO, VitrinaTeamDTO, VitrinaActivityDTO
from .mapper import map_projects, map_teams, map_activities
from .exceptions import VitrinaApiError


logger = logging.getLogger(__name__)


class VitrinaClient(BaseApiClient):
    """
    Клиент для работы с API Витрины проектов ИШИТР+.
    
    Используется для получения:
    - Проектов
    - Команд
    - Активности студентов (часы)
    """
    
    def __init__(
        self,
        base_url: str,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        mock_mode: bool = False,
        mock_path: Optional[Path] = None,
    ):
        super().__init__(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            mock_mode=mock_mode,
            mock_path=mock_path,
            client_id=client_id,
            client_secret=client_secret,
        )
    
    def _build_error(self, message: str, original_error=None):
        return VitrinaApiError(f"{message}: {original_error}")
    
    def get_projects(self) -> List[VitrinaProjectDTO]:
        """Получает список проектов"""
        logger.info("Fetching projects from Vitrina API")
        data = self.get('/projects')
        return map_projects(data)
    
    def get_teams(self) -> List[VitrinaTeamDTO]:
        """Получает список команд"""
        logger.info("Fetching teams from Vitrina API")
        data = self.get('/teams')
        return map_teams(data)
    
    def get_activities(self) -> List[VitrinaActivityDTO]:
        """Получает активность студентов (часы)"""
        logger.info("Fetching activities from Vitrina API")
        data = self.get('/activities')
        return map_activities(data)