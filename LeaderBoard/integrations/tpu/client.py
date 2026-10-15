import logging
from typing import Optional
from pathlib import Path

from ..base_client import BaseApiClient
from .dto import TPUUserDTO
from .exceptions import TPUApiError


logger = logging.getLogger(__name__)


class TPUClient(BaseApiClient):
    """Клиент для работы с API ТПУ"""

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
        return TPUApiError(f"{message}: {original_error}")

    def get_user_profile(self, user_id: int) -> Optional[TPUUserDTO]:
        """
        Получает профиль пользователя ТПУ по ID.
        
        Эндпоинт: GET /users/{targetId}
        Пример: https://tpu.community.design/dev/api/users/283991
        
        Args:
            user_id: ID пользователя в системе ТПУ (= tpu_user_id из Витрины)
            
        Returns:
            TPUUserDTO или None, если пользователь не найден
        """
        logger.info(f"Fetching TPU user profile: user_id={user_id}")
        try:
            data = self.get(f'/users/{user_id}')
            return TPUUserDTO.from_api_response(data)
        except Exception as e:
            logger.warning(f"Failed to fetch TPU user profile {user_id}: {e}")
            return None