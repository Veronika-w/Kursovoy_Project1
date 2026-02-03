import datetime
from typing import Any
from json.decoder import JSONDecodeError
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
read_excel_file_logger = logging.getLogger()
operations_card_logger = logging.getLogger()
top_five_transactions_logger = logging.getLogger()
currency_rate_logger = logging.getLogger()
currency_stocks_logger = logging.getLogger()
get_user_settings_logger = logging.getLogger()


load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_FINNHUB = os.getenv("API_KEY_FINNHUB")


now = datetime.datetime.now()

def greetings(time):
    """Приветствие, в зависимости от текущего времени."""
    greeting_by_time_of_day_logger.info('Начало работы функции, вывода приветствия')
    greeting = ""
    if time.hour < 12:
        greeting += "Доброе утро"
    elif time.hour < 18:
        greeting += "Добрый день"
    elif time.hour < 23:
        greeting += "Добрый вечер"
    else:
        greeting += "Доброй ночи"
    greeting_by_time_of_day_logger.info('Функция возвращает приветствие в зависимости от времени')
    return greeting


# greeting = greetings(now)
# print(greeting)


def filter_by_date(date: str, my_list: list) -> list:
    """Функция фильтрующая данные по заданной дате"""
    list_by_date = []
    filter_by_date_logger.info('Начало работы функции фильтрующей данные дате')
    if date == "":
        return list_by_date
    year, month, day = int(date[0:4]), int(date[5:7]), int(date[8:10])
    date_obj = datetime.datetime(year, month, day)
    for i in my_list:
        if i["Дата платежа"] == "nan" or type(i["Дата платежа"]) is float:
            continue
        elif (
                date_obj
                >= datetime.datetime.strptime(str(i["Дата платежа"]), "%d.%m.%Y")
                >= date_obj - datetime.timedelta(days=day - 1)
        ):
            list_by_date.append(i)
    filter_by_date_logger.info('Конец работы функции фильтрующей данные по дате')
    return list_by_date


def read_excel_file(excel_path: str) -> list[dict]:
    """Функция считывает финансовые операции из Excel - файла и выдает список
    словарей с транзакциями."""
    read_excel_file_logger.info('Начало работы функции считывающей excel-файл')
    try:
        df_excel = pd.read_excel(excel_path)
        df_dict_excel = df_excel.to_dict(orient="records")
        read_excel_file_logger.info('Создан список словарей финансовых транзакций')
        return df_dict_excel
    except Exception:
        read_excel_file_logger.error("Файл с транзакциями не найден")
        return []

operations = read_excel_file("../data/operations.xlsx")


def operations_card(operations: pd.DataFrame) -> list[dict]:
    """Функция выводит последние 4 цифры карты, сумму расходов и кешбэк"""
    list_transactions = []
    operations_card_logger.info('Начало работы функции с данными по карте')
    operation_sort = operations[operations["Сумма платежа"] < 0]
    operation_sort_by_group = operation_sort.groupby(["Номер карты"]).agg({"Сумма платежа": "sum"}).abs()
    operation_sort_by_value = operation_sort_by_group.sort_values(by=["Сумма платежа"], ascending=True)
    operations_card_logger.info('Формирование списка словарей с данными по картам')
    for i,some_price in operation_sort_by_value.iterrows():
        list_transactions.append({"last_digits": i,
                                  "total_spend": float(some_price["Сумма платежа"]),
                                  "cashback": float(some_price["Сумма платежа"] / 100)})
    operations_card_logger.info('Конец работы функции с данными по карте')
    return list_transactions

# pprint.pprint(operations_card(operations))


def top_five_transactions(operations: pd.DataFrame) -> list[dict]:
    """Функция, которая возвращает Топ-5 транзакций по сумме платежа"""
    list_top_transactions = []
    top_five_transactions_logger.info('Начало работы функции, выводящей топ-5 транзакций')
    operations_sort = operations.sort_values("Сумма платежа")
    top_operations = operations_sort[:5].to_dict(orient='records')
    top_five_transactions_logger.info('Формирование списка словарей топ-5 транзакций')
    for i in top_operations:
        list_top_transactions.append({"date": i["Дата платежа"],
                                  "amount": i["Сумма платежа"] * -1,
                                  "category": i["Категория"],
                                  "description": i["Описание"]})
    top_five_transactions_logger.info('Конец работы функции, выводящей топ-5 транзакцией')
    return list_top_transactions
# pprint.pprint(top_five_transactions(operations))

with open('../data/user_settings.json', 'r', encoding='utf-8') as file:
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
    currency_rate_logger.info('Начало работы функции с информацией о курсе валют')
    response = requests.request("GET", url, headers=headers, data={})
    for key, value in response.json().get("rates").items():
        currency_rates.append({"currency": key, "rates": round(1/value, 2)})
        currency_rate_logger.info("Создание списка словарей с данными о курсе валют")
    currency_rate_logger.info('Конец работы функции с информацией о курсе валют')
    return currency_rates

# if __name__ == '__main__':
#     print(currency_rate(values_to_request))


def currency_stocks(stocks: str) -> list[dict]:
    """Функция, которая выводит информацию о стоимости акций"""
    currency_stocks_logger.info('Начало работы функции с информацией об акциях')
    finnhub_client = finnhub.Client(api_key=os.getenv("API_KEY_FINNHUB"))

    stock_prices = []
    currency_stocks_logger.info("Функция обрабатывает данные транзакций.")
    for ind in stocks:
        quote = finnhub_client.quote(ind)
        currency_stocks_logger.info('Формирование списка словарей с данными об акциях')
        stock_prices.append({"stock": ind, "price": quote["c"]})
    currency_stocks_logger.info('Конец работы функции с информацией об акциях')
    return stock_prices

# if __name__ == '__main__':
#     print(currency_stocks(values_stocks_to_request))

def get_user_settings(path: str) -> list:
    """Функция принимает на вход путь до JSON-файла и возвращает список словарей с данными об валютах и акциях"""
    get_user_settings_logger.info("Начало работы функции преобразующей JSON-файл")
    try:
        with open(path, encoding="utf-8") as file:
            try:
                user_settings = json.load(file)
                get_user_settings_logger.info("Создан список словарей с данными об валютах и акциях")
                return user_settings
            except JSONDecodeError:
                get_user_settings_logger.error("Ошибка файла с транзакциями")
                return []
    except FileNotFoundError:
        get_user_settings_logger.error("Файл с транзакциями не найден")
        return []