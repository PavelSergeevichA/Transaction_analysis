import json
import logging
import os
from typing import Any

import logger
import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("logs/utils.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_operations_excel(input_file_excel) -> list:
    """Возвращает список транзакций, загруженный из файла excel"""
    df = pd.read_excel(input_file_excel)
    operations = df.where(pd.notnull(df), None).to_dict(orient="records")
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


def get_currency(user_settings: dict) -> tuple[int, str]:
    """Возвращает словарь с курсом валют"""

    url = (
        f"https://api.apilayer.com/exchangerates_data/latest?symbols="
        f"{user_settings["user_currencies"][0]}%2C%20{user_settings["user_currencies"][1]}&base=RUB"
    )

    payload = {}
    headers = {"apikey": API_KEY}

    response = requests.request("GET", url, headers=headers, data=payload)

    status_code = response.status_code
    result = response.text

    return status_code, result


def get_stocks(user_settings: dict) -> list[Any]:
    """Возвращает список словарей, где ключи - акции, а значения - их стоимость"""
    stocks = []
    for stock in user_settings["user_stocks"]:
        ticker_data = yf.Ticker(stock)
        current_price = ticker_data.info["currentPrice"]
        stocks.append({"stock" :stock, "price": current_price})
    return stocks
