import logging
import json

logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("../logs/services.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def simple_search(transactions: list[dict], users_request: str):
    """Возвращает JSON-ответ со всеми транзакциями, содержащими запрос в описании или категории"""
    if not users_request.strip():
        return json.dumps([], ensure_ascii=False)

    search_term = users_request.lower().strip()
    operations_found = []
    logger.info(f"Запрос пользователя {users_request}")

    for transaction in transactions:
        description = str(transaction.get('Описание', '') or '').lower()
        category = str(transaction.get('Категория', '') or '').lower()

        if search_term in description or search_term in category:
            operations_found.append(transaction)

    return json.dumps(operations_found, ensure_ascii=False)
