import json

from src.reports import spending_by_category
from src.services import simple_search
from utils import get_operations_excel, get_currency, open_json, get_stocks
from views import (average_spent, date_list, daypart, operation_counts,
                   sort_by_date, top_operations)


if __name__ == "__main__":
    operation_date = '20.02.2018 18:53:30'
    input_file_excel = "../data/operations.xlsx"
    input_file_user_settings = "../data/user_settings.json"
    greeting = daypart(operation_date)
    all_operations = get_operations_excel(input_file_excel=input_file_excel)
    operations = sort_by_date(all_operations, operations_date=date_list(operation_date))
    counted_operations = dict(operation_counts(operations=operations))
    cards = average_spent(operations, counted_operations)
    top_transactions = top_operations(operations)
    user_settings = open_json(input_file_user_settings)
    currency_rates = get_currency(user_settings=user_settings)
    stock_prices = get_stocks(user_settings=user_settings)

    answer = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    json_data = json.dumps(answer, ensure_ascii=False, indent=4)
    print(json_data)

    users_request = input("Введите запрос для поиска по категориям и описанию: ")
    operations_by_users_request = simple_search(transactions=operations, users_request=users_request)
    print(operations_by_users_request)

    result = spending_by_category(all_operations, 'Фастфуд', operation_date)
    print(f"Найдено записей: {len(result)}")
