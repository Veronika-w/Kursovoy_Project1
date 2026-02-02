import datetime
from typing import Any

import finnhub
import pandas as pd
import pprint
import requests
import json
import os
from dotenv import load_dotenv
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
    filename="../logs/utils.log",
    filemode="w",
)

greeting_by_time_of_day_logger = logging.getLogger()
filter_by_date_logger = logging.getLogger()
reading_excel_file_logger = logging.getLogger()
card_expenses_logger = logging.getLogger()
transaction_rating_logger = logging.getLogger()
exchange_rate_logger = logging.getLogger()
get_price_stock_logger = logging.getLogger()
get_user_settings_logger = logging.getLogger()


load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_FINNHUB = os.getenv("API_KEY_FINNHUB")


now = datetime.datetime.now()

def greetings(time):
    """Приветствие, в зависимости от текущего времени."""
    greeting = ""
    if time.hour < 12:
        greeting += "Доброе утро"
    elif time.hour < 18:
        greeting += "Добрый день"
    elif time.hour < 23:
        greeting += "Добрый вечер"
    else:
        greeting += "Доброй ночи"
    return greeting


# greeting = greetings(now)
# print(greeting)

def read_excel_file(excel_path: str) -> list[dict]:
    """Функция считывает финансовые операции из Excel - файла и выдает список
    словарей с транзакциями."""
    try:
        df_excel = pd.read_excel(excel_path)
        df_dict_excel = df_excel.to_dict(orient="records")
        return df_dict_excel
    except Exception:
        return []

operations = read_excel_file("../data/operations.xlsx")


def operations_card(operations: pd.DataFrame) -> list[dict]:
    """Функция выводит последние 4 цифры карты, сумму расходов и кешбэк"""
    list_transactions = []
    operation_sort = operations[operations["Сумма платежа"] < 0]
    operation_sort_by_group = operation_sort.groupby(["Номер карты"]).agg({"Сумма платежа": "sum"}).abs()
    operation_sort_by_value = operation_sort_by_group.sort_values(by=["Сумма платежа"], ascending=True)
    for i,some_price in operation_sort_by_value.iterrows():
        list_transactions.append({"last_digits": i,
                                  "total_spend": float(some_price["Сумма платежа"]),
                                  "cashback": float(some_price["Сумма платежа"] / 100)})
    return list_transactions

# pprint.pprint(operations_card(operations))


def top_five_transactions(operations: pd.DataFrame) -> list[dict]:
    """Функция, которая возвращает Топ-5 транзакций по сумме платежа"""
    list_top_transactions = []
    operations_sort = operations.sort_values("Сумма платежа")
    top_operations = operations_sort[:5].to_dict(orient='records')
    for i in top_operations:
        list_top_transactions.append({"date": i["Дата платежа"],
                                  "amount": i["Сумма платежа"] * -1,
                                  "category": i["Категория"],
                                  "description": i["Описание"]})
    return list_top_transactions
# pprint.pprint(top_five_transactions(operations))

with open('C:/Users/i3/my_pj/Kursovoy_Project1/data/user_settings.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

values_to_request = ", ".join(json_data ["user_currencies"])
values_stocks_to_request = (json_data ["user_stocks"])
# print(values_to_request)


def currency_rate(symbols: str) -> list[dict]:
    """Функция, которая выводит информацию о курсах валют"""
    base = "RUB"
    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={symbols}&base={base}"

    headers = {"apikey": API_KEY}
    currency_rates = []
    response = requests.request("GET", url, headers=headers, data={})
    for key, value in response.json().get("rates").items():
        currency_rates.append({"currency": key, "rates": round(1/value, 2)})
    return currency_rates

# if __name__ == '__main__':
#     print(currency_rate(values_to_request))


def currency_stocks(stocks: str) -> list[dict]:
    """Функция, которая выводит информацию о стоимости акций"""
    finnhub_client = finnhub.Client(api_key=os.getenv("API_KEY_FINNHUB"))

    stock_prices = []
    for ind in stocks:
        quote = finnhub_client.quote(ind)
        stock_prices.append({"stock": ind, "price": quote["c"]})
    return stock_prices

# if __name__ == '__main__':
#     print(currency_stocks(values_stocks_to_request))
