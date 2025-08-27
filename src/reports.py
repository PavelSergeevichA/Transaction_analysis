from datetime import datetime, timedelta
from typing import Optional

import pandas as pd


def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние три месяца (от переданной даты)"""
    if date:
        end_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S").date()
    else:
        end_date = datetime.now().date()

    # Дата начала периода (3 месяца назад)
    start_date = (end_date - timedelta(days=90)).replace(day=1)

    # Копируем и преобразуем даты
    df = transactions.copy()
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], format='%d.%m.%Y %H:%M:%S')

    # Фильтруем по категории и дате
    result = df[
        (df['Категория'] == category) &
        (df['Дата операции'] >= pd.Timestamp(start_date)) &
        (df['Дата операции'] <= pd.Timestamp(end_date))
        ]

    return result