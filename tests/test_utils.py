import json
import os
import tempfile
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import requests

from src.utils import get_currency, get_operations_excel, get_stocks, open_json


class TestGetOperationsExcel:

    def test_successful_file_loading(self):
        """Тест успешной загрузки файла с данными"""
        # Создаем временный файл Excel
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            # Создаем тестовые данные
            test_data = pd.DataFrame({
                'id': [1, 2, 3],
                'amount': [100.0, 200.0, 300.0],
                'description': ['test1', 'test2', 'test3']
            })
            test_data.to_excel(tmp.name, index=False)
            tmp_path = tmp.name

        try:
            # Вызываем функцию
            result = get_operations_excel(tmp_path)

            # Проверяем результат
            assert isinstance(result, list)
            assert len(result) == 3
            assert result[0]['id'] == 1
            assert result[1]['amount'] == 200.0
            assert result[2]['description'] == 'test3'

        finally:
            # Удаляем временный файл
            os.unlink(tmp_path)

    def test_empty_file(self):
        """Тест загрузки пустого файла"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            # Создаем пустой DataFrame
            empty_df = pd.DataFrame()
            empty_df.to_excel(tmp.name, index=False)
            tmp_path = tmp.name

        try:
            result = get_operations_excel(tmp_path)
            assert isinstance(result, list)
            assert len(result) == 0

        finally:
            os.unlink(tmp_path)

    def test_nonexistent_file(self):
        """Тест обработки несуществующего файла"""
        with pytest.raises(FileNotFoundError):
            get_operations_excel('nonexistent_file.xlsx')

    def test_wrong_file_format(self):
        """Тест обработки файла неправильного формата"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name

        try:
            with pytest.raises(Exception):
                get_operations_excel(tmp_path)
        finally:
            os.unlink(tmp_path)

    @patch('pandas.read_excel')
    def test_mock_read_excel(self, mock_read):
        """Тест с моком pandas.read_excel"""
        # Настраиваем мок
        mock_df = pd.DataFrame({
            'id': [1, 2],
            'amount': [100, 200]
        })
        mock_read.return_value = mock_df

        result = get_operations_excel('any_file.xlsx')

        # Проверяем, что read_excel был вызван
        mock_read.assert_called_once_with('any_file.xlsx')

        # Проверяем результат
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[1]['amount'] == 200


def test_open_json_success(tmp_path):
    """Тест успешного чтения корректного JSON файла"""
    # Создаем временный файл с корректным JSON
    test_data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
    test_file = tmp_path / "test.json"

    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f)

    # Вызываем функцию
    result = open_json(str(test_file))

    # Проверяем результат
    assert result == test_data
    assert isinstance(result, list)


def test_open_json_file_not_found():
    """Тест обработки несуществующего файла"""
    result = open_json("non_existent_file.json")
    assert result == []  # Должен вернуть пустой список


def test_open_json_invalid_json(tmp_path):
    """Тест обработки файла с некорректным JSON"""
    # Создаем файл с некорректным JSON
    test_file = tmp_path / "invalid.json"

    with open(test_file, 'w', encoding='utf-8') as f:
        f.write('{"invalid": json')  # Некорректный JSON

    # Вызываем функцию
    result = open_json(str(test_file))

    # Проверяем, что вернулся пустой список
    assert result == []


def test_open_json_empty_file(tmp_path):
    """Тест обработки пустого файла"""
    test_file = tmp_path / "empty.json"

    # Создаем пустой файл
    test_file.touch()

    result = open_json(str(test_file))
    assert result == []  # Пустой файл также должен вызывать ошибку JSONDecodeError


def test_open_json_empty_list(tmp_path):
    """Тест чтения файла с пустым списком"""
    test_data = []
    test_file = tmp_path / "empty_list.json"

    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f)

    # Функция ожидает список, но словарь тоже должен быть прочитан корректно
    result = open_json(str(test_file))
    assert result == test_data  # Вернет словарь, а не список


class TestGetCurrency:

    @patch('src.utils.requests.get')
    def test_successful_response(self, mock_get):
        """Тест успешного получения данных от API"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "rates": {
                "USD": 0.011,
                "EUR": 0.0095
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        user_settings = {
            "user_currencies": ["USD", "EUR"]
        }

        result = get_currency(user_settings)

        expected_result = [
            {'currency': 'USD', 'rate': round(1 / 0.011, 2)},
            {'currency': 'EUR', 'rate': round(1 / 0.0095, 2)}
        ]

        assert result == expected_result
        mock_get.assert_called_once()

        # Проверяем, что запрос был сделан с правильными параметрами
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "apikey" in kwargs["headers"]
        assert "USD" in args[0] and "EUR" in args[0]

    @patch('src.utils.requests.get')
    def test_http_error(self, mock_get):
        """Тест обработки HTTP ошибки"""
        # Мокируем HTTP ошибку
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        user_settings = {
            "user_currencies": ["USD", "EUR"]
        }

        result = get_currency(user_settings)

        # Проверяем, что функция вернула ошибку
        assert "error" in result
        assert "404 Not Found" in result["error"]

    @patch('src.utils.requests.get')
    def test_connection_error(self, mock_get):
        """Тест обработки ошибки соединения"""
        # Мокируем ошибку соединения
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        user_settings = {
            "user_currencies": ["USD", "EUR"]
        }

        result = get_currency(user_settings)

        # Проверяем, что функция вернула ошибку
        assert "error" in result
        assert "Connection failed" in result["error"]

    @patch('src.utils.requests.get')
    def test_json_parsing_error(self, mock_get):
        """Тест обработки ошибки парсинга JSON"""
        # Мокируем ответ с невалидным JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        user_settings = {
            "user_currencies": ["USD", "EUR"]
        }

        result = get_currency(user_settings)

        # Проверяем, что функция вернула ошибку парсинга
        assert "error" in result
        assert "Неверный формат ответа от API" in result["error"]


def test_get_stocks_success():
    """Тест успешного получения данных об акциях"""
    # Мокируем данные пользователя
    user_settings = {
        "user_stocks": ["AAPL", "GOOGL", "MSFT"]
    }

    # Мокируем yf.Ticker и его свойства
    mock_ticker = Mock()
    mock_ticker.info = {"currentPrice": 150.0}

    with patch('src.utils.yf.Ticker') as mock_ticker_class:
        # Настраиваем мок для возврата нашего mock_ticker
        mock_ticker_class.return_value = mock_ticker

        # Вызываем тестируемую функцию
        result = get_stocks(user_settings)

        # Проверяем результаты
        assert len(result) == 3
        assert result[0]["stock"] == "AAPL"
        assert result[0]["price"] == 150.0
        assert result[1]["stock"] == "GOOGL"
        assert result[1]["price"] == 150.0
        assert result[2]["stock"] == "MSFT"
        assert result[2]["price"] == 150.0


def test_get_stocks_single_stock():
    """Тест с одной акцией"""
    user_settings = {
        "user_stocks": ["TSLA"]
    }

    mock_ticker = Mock()
    mock_ticker.info = {"currentPrice": 250.0}

    with patch('src.utils.yf.Ticker') as mock_ticker_class:
        with patch('src.utils.logger') as mock_logger:
            mock_ticker_class.return_value = mock_ticker

            result = get_stocks(user_settings)

            assert len(result) == 1
            assert result[0]["stock"] == "TSLA"
            assert result[0]["price"] == 250.0
            mock_logger.info.assert_called_once()


def test_get_stocks_none_price():
    """Тест с None в качестве цены"""
    user_settings = {
        "user_stocks": ["AAPL"]
    }

    mock_ticker = Mock()
    mock_ticker.info = {"currentPrice": None}

    with patch('src.utils.yf.Ticker') as mock_ticker_class:
        mock_ticker_class.return_value = mock_ticker

        result = get_stocks(user_settings)

        assert len(result) == 1
        assert result[0]["stock"] == "AAPL"
        assert result[0]["price"] is None
