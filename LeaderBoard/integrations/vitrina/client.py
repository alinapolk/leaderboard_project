import logging
from pathlib import Path
from typing import List, Optional, Tuple

from ..base_client import BaseApiClient
from .dto import VitrinaProjectDTO, VitrinaActivityDTO
from .mapper import (
    map_projects,
    map_activities,
    get_total_from_response
)
from .exceptions import VitrinaApiError


logger = logging.getLogger(__name__)


class VitrinaClient(BaseApiClient):
    """Клиент для работы с API Витрины проектов ИШИТР+"""

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

    def get_projects(
        self,
        q: str = "",
        status: str = None,
        sort: str = "created_desc",
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[VitrinaProjectDTO], int]:
        """
        Получает одну страницу проектов с query-параметрами.
        
        Реальный эндпоинт:
        /projects?q=&status=Recruiting&sort=created_desc&limit=20&offset=0
        """
        params = {
            'q': q,
            'sort': sort,
            'limit': limit,
            'offset': offset,
        }
        if status:
            params['status'] = status

        logger.info(f"Fetching projects: {params}")
        data = self.get('/projects', params=params)

        projects = map_projects(data)
        total = get_total_from_response(data)

        logger.info(f"Fetched {len(projects)} projects, total={total}")
        return projects, total

            
    def get_all_projects(
        self,
        page_size: int = 20,
        status: str = None,
        sort: str = "created_desc",
        max_pages: int = 100,
    ) -> List[VitrinaProjectDTO]:
        """
        Получает ВСЕ проекты, итерируясь по страницам.
        Используется для полной синхронизации.
        
        В мок-режиме сразу возвращает все проекты из файла,
        без пагинации (мок-файл уже содержит полный ответ).
        """
        # В мок-режиме файл содержит все проекты сразу
        if self.mock_mode:
            logger.info("Mock mode: fetching all projects from mock file")
            data = self.get('/projects')
            return map_projects(data)

        all_projects = []
        offset = 0
        total = None
        pages_fetched = 0

        while pages_fetched < max_pages:
            batch, batch_total = self.get_projects(
                status=status,
                sort=sort,
                limit=page_size,
                offset=offset,
            )

            if total is None:
                total = batch_total
                logger.info(f"Total projects to fetch: {total}")

            all_projects.extend(batch)
            pages_fetched += 1
            logger.info(f"Fetched {len(all_projects)}/{total} projects (page {pages_fetched})")

            # Условия остановки
            if len(all_projects) >= total or not batch:
                break

            offset += page_size

        logger.info(f"Total projects fetched: {len(all_projects)}")
        return all_projects

    def get_activities(self) -> List[VitrinaActivityDTO]:
        """
        Получает активность студентов (часы).
        
        Пока заглушка — эндпоинт будет уточнён отдельно.
        """
        logger.info("Fetching activities from Vitrina API")
        try:
            data = self.get('/activities')
            return map_activities(data)
        except Exception as e:
            logger.warning(f"Activities endpoint not available yet: {e}")
            return []