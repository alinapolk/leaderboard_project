import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import requests
from requests.exceptions import RequestException, Timeout


logger = logging.getLogger(__name__)


class BaseApiClient:
    """
    Базовый клиент для работы с внешними API.
    
    Поддерживает:
    - Таймауты
    - Повторные попытки при ошибках
    - Логирование запросов
    - Режим работы с моками (для разработки)
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 2,
        mock_mode: bool = False,
        mock_path: Optional[Path] = None,
        auth_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.mock_mode = mock_mode
        self.mock_path = mock_path
        self.auth_token = auth_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = requests.Session()
    
    def _get_headers(self, extra_headers: Optional[Dict] = None) -> Dict[str, str]:
        """Формирует заголовки запроса"""
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        if self.client_id and self.client_secret:
            # OAuth2 client credentials
            headers['X-Client-ID'] = self.client_id
        
        if extra_headers:
            headers.update(extra_headers)
        
        return headers
    
    def _load_mock(self, endpoint: str) -> Any:
        """Загружает моковые данные из файла"""
        if not self.mock_path:
            raise ValueError("Mock path is not set")
        
        # Ищем файл мока по имени endpoint
        mock_file = self.mock_path / f"{endpoint.strip('/')}.json"
        if not mock_file.exists():
            # Пробуем общий файл
            mock_file = self.mock_path / f"{self.mock_path.name}-mock.json"
        
        if not mock_file.exists():
            raise FileNotFoundError(f"Mock file not found: {mock_file}")
        
        with open(mock_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        extra_headers: Optional[Dict] = None,
    ) -> Any:
        """
        Выполняет HTTP-запрос с повторными попытками.
        
        Возвращает JSON-ответ.
        """
        # Режим моков для разработки
        if self.mock_mode:
            logger.info(f"[MOCK] {method} {endpoint}")
            return self._load_mock(endpoint)
        
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        headers = self._get_headers(extra_headers)
        
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Request: {method} {url} (attempt {attempt}/{self.max_retries})")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=self.timeout,
                )
                
                # Логируем статус
                logger.info(f"Response: {response.status_code}")
                
                # Проверяем на ошибки HTTP
                response.raise_for_status()
                
                return response.json()
            
            except Timeout as e:
                last_error = e
                logger.warning(f"Timeout on attempt {attempt}: {e}")
            
            except RequestException as e:
                last_error = e
                logger.warning(f"Request error on attempt {attempt}: {e}")
            
            if attempt < self.max_retries:
                delay = self.retry_delay * attempt
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
        
        # Все попытки исчерпаны
        raise self._build_error(
            message=f"Request failed after {self.max_retries} attempts",
            original_error=last_error,
        )
    
    def _build_error(self, message: str, original_error: Optional[Exception] = None):
        """Создаёт исключение для наследников"""
        return RequestException(f"{message}: {original_error}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Any:
        return self._request('GET', endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Any:
        return self._request('POST', endpoint, data=data, **kwargs)