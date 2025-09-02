import logging
import json
from functools import wraps
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

logger = logging.getLogger("reports")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("../logs/reports.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def report_to_file(filename=None):
    """
    Декоратор для записи результатов функции-отчета в файл.

    Args:
        filename (str, optional): Имя файла для записи. Если None,
                                используется имя по умолчанию.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Вызываем оригинальную функцию
            result = func(*args, **kwargs)

            # Определяем имя файла
            if filename is None:
                # Формируем имя файла по умолчанию
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                default_filename = f"report_{func.__name__}_{current_time}.json"
                file_to_use = default_filename
            else:
                file_to_use = filename

            try:
                # Записываем результат в файл
                if isinstance(result, pd.DataFrame):
                    # Для DataFrame сохраняем в формате JSON
                    result.to_json(file_to_use, orient='records', indent=2,
                                   date_format='iso', force_ascii=False)
                else:
                    # Для других типов данных
                    with open(file_to_use, 'w', encoding='utf-8') as f:
                        if isinstance(result, (dict, list)):
                            json.dump(result, f, ensure_ascii=False, indent=2)
                        else:
                            f.write(str(result))

                logger.info(f"Отчет успешно сохранен в файл: {file_to_use}")

            except Exception as e:
                logger.error(f"Ошибка при записи в файл {file_to_use}: {e}")

            return result

        return wrapper

    return decorator


@report_to_file()
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние три месяца (от переданной даты)"""
    if date:
        end_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S").date()
        logger.info(f"Дата {date} получена")
    else:
        end_date = datetime.now().date()
        logger.info(f"Использована текущая дата {end_date}")

    # Дата начала периода (3 месяца назад)
    start_date = (end_date - timedelta(days=90)).replace(day=1)

    # Создаем DataFrame из списка transactions
    if isinstance(transactions, list):
        # Предполагаем, что список содержит словари с данными транзакций
        df = pd.DataFrame(transactions)
    else:
        # Если уже DataFrame, просто копируем
        df = transactions.copy()

    # Копируем и преобразуем даты
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], format='%d.%m.%Y %H:%M:%S')

    # Фильтруем по категории и дате
    result = df[
        (df['Категория'] == category)
        & (df['Дата операции'] >= pd.Timestamp(start_date))
        & (df['Дата операции'] <= pd.Timestamp(end_date))
    ]
    logger.info("Фильтрация прошла успешно")

    return result
