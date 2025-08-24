from datetime import datetime, timedelta
from typing import Optional

import pandas as pd


def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние три месяца (от переданной даты)"""
    # Определяем дату отсчета
    if date is None:
        current_date = datetime.now().date()
    else:
        current_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S").date()
    # Вычисляем дату начала периода (3 месяца назад)
    start_date = (current_date - timedelta(days=90)).replace(day=1)
    # Конвертируем даты в Timestamp для сравнения
    start_timestamp = pd.Timestamp(start_date)
    end_timestamp = pd.Timestamp(current_date)

    # Создаем копию DataFrame для безопасной работы
    transactions = transactions.copy()

    # Конвертируем столбец с датами в datetime, если это еще не сделано
    if not pd.api.types.is_datetime64_any_dtype(transactions['Дата операции']):
        transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'], format='%d.%m.%Y %H:%M:%S')

    # Фильтруем транзакции по категории и дате
    mask = (
            (transactions['Категория'] == category) &
            (transactions['Дата операции'] >= start_timestamp) &
            (transactions['Дата операции'] <= end_timestamp)
    )

    return transactions[mask].copy()
