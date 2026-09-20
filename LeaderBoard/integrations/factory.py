from pathlib import Path
from django.conf import settings

from .tpu import TPUClient
from .vitrina import VitrinaClient


def get_tpu_client() -> TPUClient:
    """Создаёт клиент ТПУ с настройками из settings"""
    return TPUClient(
        base_url=settings.TPU_API_BASE_URL,
        client_id=settings.TPU_CLIENT_ID or None,
        client_secret=settings.TPU_CLIENT_SECRET or None,
        mock_mode=settings.TPU_API_MOCK_MODE,
        mock_path=settings.TPU_API_MOCK_PATH if settings.TPU_API_MOCK_MODE else None,
    )


def get_vitrina_client() -> VitrinaClient:
    """Создаёт клиент Витрины с настройками из settings"""
    return VitrinaClient(
        base_url=settings.VITRINA_API_BASE_URL,
        client_id=settings.VITRINA_CLIENT_ID or None,
        client_secret=settings.VITRINA_CLIENT_SECRET or None,
        mock_mode=settings.VITRINA_API_MOCK_MODE,
        mock_path=settings.VITRINA_API_MOCK_PATH if settings.VITRINA_API_MOCK_MODE else None,
    )