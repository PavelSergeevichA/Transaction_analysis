import json

from src.services import simple_search


def test_simple_search_empty_request():
    """Тест на пустой запрос"""
    transactions = [
        {"Описание": "Покупка продуктов", "Категория": "Еда", "Сумма": 1000},
        {"Описание": "Оплата интернета", "Категория": "Коммунальные", "Сумма": 500}
    ]

    result = simple_search(transactions, "")
    assert result == json.dumps([], ensure_ascii=False)


def test_simple_search_whitespace_request():
    """Тест на запрос из пробелов"""
    transactions = [
        {"Описание": "Покупка продуктов", "Категория": "Еда", "Сумма": 1000}
    ]

    result = simple_search(transactions, "   ")
    assert result == json.dumps([], ensure_ascii=False)


def test_simple_search_by_description():
    """Тест поиска по описанию"""
    transactions = [
        {"Описание": "Покупка продуктов", "Категория": "Еда", "Сумма": 1000},
        {"Описание": "Оплата интернета", "Категория": "Коммунальные", "Сумма": 500},
        {"Описание": "Такси домой", "Категория": "Транспорт", "Сумма": 300}
    ]

    result = simple_search(transactions, "продуктов")
    expected = [transactions[0]]
    assert json.loads(result) == expected
