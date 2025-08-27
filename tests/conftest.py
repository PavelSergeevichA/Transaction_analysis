import pytest
import logging

@pytest.fixture(autouse=True)
def setup_logging():
    """Настройка логирования для тестов"""
    logging.basicConfig(level=logging.INFO)


@pytest.fixture
def sample_user_settings():
    return {
        "user_stocks": ["AAPL", "GOOGL", "MSFT"]
    }