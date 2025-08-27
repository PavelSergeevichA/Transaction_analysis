import re
from collections import Counter
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd


def daypart(operation_date: str) -> str:
    """Отдает нужное приветствие, в зависимости от времени"""
    if 6 <= int(operation_date[11:13]) < 12:
        return "Доброе утро"
    elif 12 <= int(operation_date[11:13]) < 18:
        return "Добрый день"
    elif 18 <= int(operation_date[11:13]) < 24:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def sort_by_date(
    operations: list, operations_date: list, reverse: bool = False
) -> list:
    """Возвращает новый список, отсортированный по ключу - списку дат"""
    operations_this_month = []
    for operation in operations:
        for operation_date in operations_date:
            if re.search(
                operation_date[:10], operation["Дата операции"], re.IGNORECASE
            ):
                operations_this_month.append(operation)
            else:
                continue
    df = pd.DataFrame(operations_this_month)
    df = df.replace({np.nan: None})
    data_cleaned = df.to_dict("records")
    return data_cleaned


def date_list(operation_date_str: str) -> list:
    """Возвращает список с диапазоном дат от первого числа месяца до указанной даты"""
    operation_date = datetime.strptime(operation_date_str, "%d.%m.%Y %H:%M:%S")
    start_date = operation_date.replace(day=1)
    dates = []
    current_date = start_date
    while current_date <= operation_date:
        dates.append(current_date.strftime("%d.%m.%Y %H:%M:%S"))
        current_date += timedelta(days=1)
    return dates


def operation_counts(operations: list) -> Counter[Any]:
    """Возвращает список словарей, где ключ - номер карты, значение - количество операций по этой карте"""
    for operation in operations:
        if operation["Номер карты"] is None:
            operations.remove(operation)
            continue
        else:
            continue
    keys_to_count = [d["Номер карты"] for d in operations]
    counted_operations = Counter(keys_to_count)
    return counted_operations


def average_spent(operations: list, counted_operations: dict) -> list:
    """Возвращает список словарей с данными о последних цифрах номера карты и сумме операций и кэшбэка"""
    card_numbers = []
    for key in counted_operations:
        if key is not None:
            card_numbers.append(key)
        else:
            continue

    card_1 = []
    card_2 = []
    for operation in operations:
        if operation["Номер карты"] == card_numbers[0]:
            card_1.append(operation["Сумма операции"])
        elif operation["Номер карты"] == card_numbers[1]:
            card_2.append(operation["Сумма операции"])

    return [
        {
            "last_digits": card_numbers[0][1:],
            "total_spent": round(-sum(card_1), 2),
            "cashback": round(-sum(card_1) / 100, 2),
        },
        {
            "last_digits": card_numbers[1][1:],
            "total_spent": round(-sum(card_2), 2),
            "cashback": round(-sum(card_2) / 100, 2),
        },
    ]


def top_operations(operations: list, reverse=True) -> list:
    """Возвращает 5 самых крупных операций"""

    operations = sorted(operations, key=lambda operation: operation['Сумма операции'], reverse=True)[:5]
    top_5_operations = [
        {key: d[key] for key in ["Дата платежа", "Сумма операции", "Категория", "Описание"]}
        for d in operations
    ]
    return top_5_operations
