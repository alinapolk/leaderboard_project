import logging
from pathlib import Path
from typing import List, Optional

from ..base_client import BaseApiClient
from .dto import TPUStudentDTO, TPUUserDTO
from .mapper import map_tpu_response_to_students
from .exceptions import TPUApiError


logger = logging.getLogger(__name__)


class TPUClient(BaseApiClient):
    """
    Клиент для работы с API ТПУ.
    
    Используется для получения данных о студентах:
    - ФИО, группа, курс
    - Успеваемость
    - Долги
    
    Пример использования:
    
        client = TPUClient(
            base_url="https://api.tpu.ru/v1",
            client_id="xxx",
            client_secret="yyy",
        )
        students = client.get_students()
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
        return TPUApiError(f"{message}: {original_error}")
    
    def get_students(self) -> List[TPUStudentDTO]:
        """
        Получает список всех студентов из API ТПУ.
        
        Возвращает список TPUStudentDTO.
        """
        logger.info("Fetching students from TPU API")
        data = self.get('/students')
        return map_tpu_response_to_students(data)
    
    def get_student_by_login(self, login: str) -> Optional[TPUStudentDTO]:
        """Получает студента по логину"""
        logger.info(f"Fetching student {login} from TPU API")
        data = self.get(f'/students/{login}')
        students = map_tpu_response_to_students([data])
        return students[0] if students else None
    
    def get_user_profile(self, user_id: int) -> Optional[TPUUserDTO]:
        """
        Получает профиль пользователя ТПУ по ID.

        Эндпоинт: GET /users/{targetId}
        Пример: https://tpu.community.design/dev/api/users/283991

        Args:
            user_id: ID пользователя в системе ТПУ (= places из Витрины)

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