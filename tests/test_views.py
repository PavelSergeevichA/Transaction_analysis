from collections import Counter

import pytest

from src.views import average_spent, date_list, daypart, operation_counts, sort_by_date, top_operations


@pytest.mark.parametrize("time_str, expected", [
    # Утро (6:00 - 11:59)
    ("2023-01-01 06:00:00", "Доброе утро"),
    ("2023-01-01 08:30:00", "Доброе утро"),
    ("2023-01-01 11:59:59", "Доброе утро"),

    # День (12:00 - 17:59)
    ("2023-01-01 12:00:00", "Добрый день"),
    ("2023-01-01 15:30:00", "Добрый день"),
    ("2023-01-01 17:59:59", "Добрый день"),

    # Вечер (18:00 - 23:59)
    ("2023-01-01 18:00:00", "Добрый вечер"),
    ("2023-01-01 20:30:00", "Добрый вечер"),
    ("2023-01-01 23:59:59", "Добрый вечер"),

    # Ночь (0:00 - 5:59)
    ("2023-01-01 00:00:00", "Доброй ночи"),
    ("2023-01-01 03:30:00", "Доброй ночи"),
    ("2023-01-01 05:59:59", "Доброй ночи"),

    # Граничные случаи
    ("2023-01-01 06:00:00", "Доброе утро"),
    ("2023-01-01 12:00:00", "Добрый день"),
    ("2023-01-01 18:00:00", "Добрый вечер"),
    ("2023-01-01 00:00:00", "Доброй ночи"),
])
def test_daypart(time_str, expected):
    """Тестирование функции daypart с различными временами"""
    assert daypart(time_str) == expected


# Тестовые данные
SAMPLE_OPERATIONS = [
    {"Дата операции": "2024-01-15 10:30:00", "Сумма": 100, "Описание": "Покупка 1"},
    {"Дата операции": "2024-01-20 14:45:00", "Сумма": 200, "Описание": "Покупка 2"},
    {"Дата операции": "2024-02-05 09:15:00", "Сумма": 300, "Описание": "Покупка 3"},
    {"Дата операции": "2024-02-10 16:20:00", "Сумма": 400, "Описание": "Покупка 4"},
    {"Дата операции": "2024-03-01 11:00:00", "Сумма": 500, "Описание": "Покупка 5"},
]


def test_sort_by_date_single_date():
    """Тест фильтрации по одной дате"""
    dates = ["2024-01-15"]
    result = sort_by_date(SAMPLE_OPERATIONS, dates)

    assert len(result) == 1
    assert result[0]["Дата операции"] == "2024-01-15 10:30:00"
    assert result[0]["Сумма"] == 100


def test_sort_by_date_multiple_dates():
    """Тест фильтрации по нескольким датам"""
    dates = ["2024-01-15", "2024-01-20"]
    result = sort_by_date(SAMPLE_OPERATIONS, dates)

    assert len(result) == 2
    dates_in_result = [op["Дата операции"][:10] for op in result]
    assert "2024-01-15" in dates_in_result
    assert "2024-01-20" in dates_in_result


def test_sort_by_date_month_filter():
    """Тест фильтрации по месяцу"""
    dates = ["2024-02"]  # Фильтр по всему месяцу
    result = sort_by_date(SAMPLE_OPERATIONS, dates)

    assert len(result) == 2
    for operation in result:
        assert operation["Дата операции"].startswith("2024-02")


def test_sort_by_date_no_matches():
    """Тест, когда нет совпадений"""
    dates = ["2024-12-25"]  # Дата, которой нет в данных
    result = sort_by_date(SAMPLE_OPERATIONS, dates)

    assert len(result) == 0
    assert result == []


def test_sort_by_date_empty_input():
    """Тест с пустыми входными данными"""
    result = sort_by_date([], ["2024-01-15"])
    assert result == []

    result = sort_by_date(SAMPLE_OPERATIONS, [])
    assert result == []


def test_sort_by_date_case_insensitive():
    """Тест регистронезависимого поиска"""
    # Создаем данные с разным регистром
    operations_with_case = [
        {"Дата операции": "2024-01-15 10:30:00", "Сумма": 100},
        {"Дата операции": "2024-01-15T10:30:00", "Сумма": 200},  # Разный формат
    ]

    dates = ["2024-01-15"]
    result = sort_by_date(operations_with_case, dates)

    assert len(result) == 2


def test_date_list_single_day():
    """Тест для одного дня в месяце"""
    result = date_list("01.01.2023 00:00:00")
    expected = ["01.01.2023 00:00:00"]
    assert result == expected


def test_date_list_first_day():
    """Тест для первого дня месяца"""
    result = date_list("01.05.2023 12:30:45")
    expected = ["01.05.2023 12:30:45"]
    assert result == expected


def test_date_list_middle_of_month():
    """Тест для середины месяца"""
    result = date_list("15.03.2023 15:45:30")
    assert len(result) == 15
    assert result[0] == "01.03.2023 15:45:30"  # первый день
    assert result[-1] == "15.03.2023 15:45:30"  # последний день


def test_operation_counts_basic():
    """Тест базового функционала - подсчет операций по картам"""
    operations = [
        {"Номер карты": "1234", "Сумма": 100},
        {"Номер карты": "5678", "Сумма": 200},
        {"Номер карты": "1234", "Сумма": 300},
        {"Номер карты": "9012", "Сумма": 400},
    ]

    result = operation_counts(operations)

    expected = Counter({"1234": 2, "5678": 1, "9012": 1})
    assert result == expected


def test_operation_counts_with_none():
    """Тест с None значениями в номерах карт"""
    operations = [
        {"Номер карты": "1234", "Сумма": 100},
        {"Номер карты": None, "Сумма": 200},  # должен быть удален
        {"Номер карты": "5678", "Сумма": 300},
        {"Номер карты": None, "Сумма": 400},  # должен быть удален
        {"Номер карты": "1234", "Сумма": 500},
    ]

    result = operation_counts(operations)

    expected = Counter({"1234": 2, "5678": 1})
    assert result == expected


def test_operation_counts_all_none():
    """Тест когда все номера карт None"""
    operations = [
        {"Номер карты": None, "Сумма": 100},
        {"Номер карты": None, "Сумма": 200},
        {"Номер карты": None, "Сумма": 300},
    ]

    result = operation_counts(operations)

    expected = Counter()
    assert result == expected


def test_operation_counts_empty_list():
    """Тест с пустым списком операций"""
    operations = []

    result = operation_counts(operations)

    expected = Counter()
    assert result == expected


def test_operation_counts_single_card():
    """Тест с одной картой и множеством операций"""
    operations = [
        {"Номер карты": "9999", "Сумма": 100},
        {"Номер карты": "9999", "Сумма": 200},
        {"Номер карты": "9999", "Сумма": 300},
        {"Номер карты": "9999", "Сумма": 400},
    ]

    result = operation_counts(operations)

    expected = Counter({"9999": 4})
    assert result == expected


def test_average_spent_basic():
    """Тест базового функционала функции"""
    operations = [
        {"Номер карты": "1234567812345678", "Сумма операции": -100.0},
        {"Номер карты": "1234567812345678", "Сумма операции": -200.0},
        {"Номер карты": "8765432187654321", "Сумма операции": -300.0},
        {"Номер карты": "8765432187654321", "Сумма операции": -400.0},
    ]

    counted_operations = {
        "1234567812345678": 2,
        "8765432187654321": 2,
        None: 0
    }

    result = average_spent(operations, counted_operations)

    assert len(result) == 2
    assert result[0]["last_digits"] == "234567812345678"
    assert result[0]["total_spent"] == 300.0
    assert result[0]["cashback"] == 3.0

    assert result[1]["last_digits"] == "765432187654321"
    assert result[1]["total_spent"] == 700.0
    assert result[1]["cashback"] == 7.0
