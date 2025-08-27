import json
import logging
import os
from typing import Any

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("D:/Projects/Transaction_analysis/logs/utils.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_operations_excel(input_file_excel) -> list:
    """Возвращает список транзакций, загруженный из файла excel"""
    df = pd.read_excel(input_file_excel)
    operations = df.where(pd.notnull(df), None).to_dict(orient="records")
    logger.info(f"Файл {input_file_excel} открыт")
    return operations


def open_json(input_file) -> list:
    """Возвращает данные из json файла"""
    logger.info(f"Начало обработки файла: {input_file}")
    data = []
    try:
        with open(input_file, encoding="utf-8") as f:
            data = json.load(f)
            logger.info("Данные с файла сохранены в словарь")
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error("Файл не найден, не удалось распознать содержимое файла")
        return data


def get_currency(user_settings: dict[str, Any]) -> dict[str, Any]:
    """Возвращает словарь с курсом валют"""

    url = (
        f"https://api.apilayer.com/exchangerates_data/latest?symbols="
        f"{user_settings['user_currencies'][0]},{user_settings['user_currencies'][1]}&base=RUB"
    )

    headers = {"apikey": API_KEY}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверяем статус ответа

        result = response.json()  # Преобразуем в словарь
        logger.info("Данные API получены успешно")

        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении данных: {e}")
        return {"error": f"Ошибка API: {str(e)}"}
    except ValueError as e:
        logger.error(f"Ошибка парсинга JSON: {e}")
        return {"error": "Неверный формат ответа от API"}


def get_stocks(user_settings: dict) -> list[Any]:
    """Возвращает список словарей, где ключи - акции, а значения - их стоимость"""
    stocks = []
    for stock in user_settings["user_stocks"]:
        ticker_data = yf.Ticker(stock)
        current_price = ticker_data.info["currentPrice"]
        stocks.append({"stock" :stock, "price": current_price})
        logger.info(f"Данные о стоимости акций {user_settings["user_stocks"]} получены")
    return stocks
