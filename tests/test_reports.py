import pandas as pd

from src.reports import spending_by_category


def test_spending_by_category_basic():
    """Тест базовой функциональности"""
    # Создаем тестовые данные
    test_data = pd.DataFrame({
        'Дата операции': ['01.01.2024 12:00:00', '15.02.2024 12:00:00', '20.03.2024 12:00:00'],
        'Категория': ['Продукты', 'Продукты', 'Транспорт'],
        'Сумма': [1000, 1500, 500]
    })

    result = spending_by_category(test_data, 'Продукты', '31.03.2024 23:59:59')

    # Проверяем, что вернулись только записи с категорией "Продукты"
    assert len(result) == 2
    assert all(result['Категория'] == 'Продукты')
    assert set(result['Сумма'].tolist()) == {1000, 1500}
