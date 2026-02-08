import json
import logging
import os
from json import JSONDecodeError

from src.utils import (currency_rate, currency_stocks, filter_by_date, get_date_time, greetings, operations_card,
                       top_five_transactions)

logger = logging.getLogger("views")
log = os.path.join(os.path.dirname(__file__), "..", "logs", "views.log")
file_handler = logging.FileHandler(
    os.path.join(os.path.dirname(__file__), "../logs/views.log"),
    "w",
    encoding="utf-8",
)
file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def greetings_info(date_time: str) -> str:
    """Приветствие пользователя в зависимости от его времени суток"""
    greeting = greetings()
    time_period = get_date_time(date_time)
    sorted_df = filter_by_date(
        os.path.join(os.path.dirname(__file__), "../data/operations.xlsx"),
        time_period,
    )
    cards = operations_card(sorted_df)
    top_transactions = top_five_transactions(sorted_df)
    currency_rates = currency_rate()
    stock_prices = currency_stocks()
    try:
        logger.info("получение и формирование json-ответа")
        data = {
            "greeting": greeting,
            "cards": cards,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        }

        json_data = json.dumps(data, ensure_ascii=False, indent=4)

        logger.info("успешно сформирован ответ")
        return json_data

    except JSONDecodeError:
        logger.error("Произошла ошибка кодирования")
        return "ошибка формирования ответа"
