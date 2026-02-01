import json
import logging
from src.utils import greetings, filter_by_date, read_excel_file, operations_card
from src.utils import top_five_transactions, currency_rate, currency_stocks, now, get_user_settings


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
    filename="../logs/views.log",
    filemode="w",
)

main_logger = logging.getLogger()

my_list = read_excel_file("../data/operations.xlsx")
user_settings = get_user_settings("../data/user_settings.json")
stocks = user_settings["user_stocks"]
currency = user_settings["user_currencies"]


def main(user_data: str, stocks: dict, currency: dict) -> str:
    """Функция создающая JSON ответ для страницы главная"""
    main_logger.info('Начало работы функции main')
    final_list = filter_by_date(user_data, my_list)
    greeting = greetings(now)
    cards = operations_card(final_list)
    top_trans = top_five_transactions(final_list)
    stocks_prices = currency_stocks(stocks)
    currency_r = currency_rate(currency)
    main_logger.info('Формирование JSON ответа')
    result = [{
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_trans,
        "currency_rates": currency_r,
        "stock_prices": stocks_prices,
    }]
    date_json = json.dumps(
        result,
        indent=4,
        ensure_ascii=False,
    )
    main_logger.info("Завершение работы функции main")
    return date_json


print(main('2021-10-20', stocks, currency))