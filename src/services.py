import json


def simple_search(transactions: list[dict], users_request: str):
    """Возвращает JSON-ответ со всеми транзакциями, содержащими запрос в описании или категории"""
    if not users_request.strip():
        return json.dumps([], ensure_ascii=False)

    search_term = users_request.lower().strip()
    operations_found = []

    for transaction in transactions:
        description = transaction.get('Описание', '').lower()
        category = transaction.get('Категория', '').lower()

        if search_term in description or search_term in category:
            operations_found.append(transaction)

    return json.dumps(operations_found, ensure_ascii=False)
