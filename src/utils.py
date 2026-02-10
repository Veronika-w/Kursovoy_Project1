import datetime
import json
import logging
import os
import pprint
from json.decoder import JSONDecodeError
from typing import Any

import finnhub
import pandas as pd
import requests
from dotenv import load_dotenv

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


date_now = datetime.datetime.now()


def greetings(date_now: datetime) -> str:
    """Приветствие, в зависимости от текущего времени."""
    greeting_by_time_of_day_logger.info("Начало работы функции, вывода приветствия")
    hour = date_now.hour
    if 6 <= hour < 12:
        greeting = "Доброе утро!"
    elif 12 <= hour < 18:
        greeting = "Добрый день!"
    elif 18 <= hour < 23:
        greeting = "Добрый вечер!"
    else:
        greeting = "Доброй ночи!"
    greeting_by_time_of_day_logger.info("Функция возвращает приветствие в зависимости от времени")
    return greeting


# greeting = greetings(now)
# print(greeting)


def get_date_time(date_time: str, date_format: str = "%Y-%m-%d %H:%M:%S") -> list[str]:
    """Меняет формат строки и фильтрует от начала месяца до указанного числа"""
    dt = datetime.strptime(date_time, date_format)
    month_start = dt.replace(day=1)

    return [month_start.strftime("%d.%m.%Y %H:%M:%S"), dt.strftime("%d.%m.%Y %H:%M:%S")]


def read_excel_file(excel_path: str) -> list[dict]:
    """Функция считывает финансовые операции из Excel - файла и выдает список
    словарей с транзакциями."""
    read_excel_file_logger.info("Начало работы функции считывающей excel-файл")
    try:
        df_excel = pd.read_excel(excel_path)
        df_dict_excel = df_excel.to_dict(orient="records")
        read_excel_file_logger.info("Создан список словарей финансовых транзакций")
        return df_dict_excel
    except FileNotFoundError:
        read_excel_file_logger.error("Файл с транзакциями не найден")
        return []


operations = read_excel_file("../data/operations.xlsx")


def filter_by_date(date: str, my_list: list) -> list:
    """Функция фильтрующая данные по заданной дате"""
    list_by_date = []
    filter_by_date_logger.info("Начало работы функции фильтрующей данные дате")
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
    filter_by_date_logger.info("Конец работы функции фильтрующей данные по дате")
    return list_by_date


# f = pd.DataFrame(read_excel_file("../data/operations.xlsx"))
# print('20.08.2020', f)


def operations_card(my_list: list) -> Any:
    """Функция выводит последние 4 цифры карты, сумму расходов и кешбэк"""
    cards = {}
    information_on_cards = []
    operations_card_logger.info("Начало работы функции с данными по карте")

    for transaction in my_list:
        if transaction["Номер карты"] == "nan" or type(transaction["Номер карты"]) is float:
            continue
        elif transaction["Сумма платежа"] == "nan":
            continue
        else:
            if transaction["Номер карты"][1:] in cards:
                cards[transaction["Номер карты"][1:]] += float(str(transaction["Сумма платежа"])[1:])
            else:
                cards[transaction["Номер карты"][1:]] = float(str(transaction["Сумма платежа"])[1:])
    operations_card_logger.info("Формирование списка словарей с данными по картам")
    for k, v in cards.items():
        information_on_cards.append({"last_digits": k, "total_spent": round(v, 2), "cashback": round(v / 100, 2)})
    operations_card_logger.info("Конец работы функции с данными по карте")
    return information_on_cards


# f = pd.DataFrame(read_excel_file("../data/operations.xlsx"))
# print(operations_card(f))


def top_five_transactions(my_list: list) -> list[dict]:
    """Функция, которая возвращает Топ-5 транзакций по сумме платежа"""
    all_expenses = []
    top_five_transaction = []
    top_five_transactions_logger.info("Начало работы функции выводящей топ-5 транзакций")
    for transaction in my_list:
        if transaction["Категория"] != "Пополнения":
            all_expenses.append(transaction)
        else:
            continue
    sorted_transactions = sorted(all_expenses, key=lambda x: x["Сумма платежа"], reverse=True)[:5]
    top_five_transactions_logger.info("Формирование списка словарей топ-5 транзакций")
    for transaction in sorted_transactions:
        top_five_transaction.append(
            {
                "date": transaction["Дата платежа"],
                "amount": transaction["Сумма платежа"],
                "category": transaction["Категория"],
                "description": transaction["Описание"],
            }
        )
    top_five_transactions_logger.info("Конец работы функции выводящей топ-5 транзакцийе")
    return top_five_transaction


# f = pd.DataFrame(read_excel_file("../data/operations.xlsx"))
# print(top_five_transactions(f))


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


def currency_rate(currency: dict) -> list[dict]:
    """Функция, которая выводит информацию о курсах валют"""
    try:
        base = "RUB"
        url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={currency}&base={base}"

        headers = {"apikey": API_KEY}
        currency_rates = []
        currency_rate_logger.info("Начало работы функции с информацией о курсе валют")
        response = requests.request("GET", url, headers=headers, data={})
        for key, value in response.json().get("rates").items():
            currency_rates.append({"currency": key, "rates": round(1 / value, 2)})
            currency_rate_logger.info("Создание списка словарей с данными о курсе валют")
        currency_rate_logger.info("Конец работы функции с информацией о курсе валют")
        return currency_rates
    except Exception as e:
        print(f"Ошибка конвертации: {e}")
        return 0.0


if __name__ == "__main__":
    with open("../data/user_settings.json", "r", encoding="utf-8") as file:
        json_data = json.load(file)
    values_to_request = ", ".join(json_data["user_currencies"])
    print(currency_rate(values_to_request))


def currency_stocks(stocks: dict) -> list[dict]:
    """Функция, которая выводит информацию о стоимости акций"""
    currency_stocks_logger.info("Начало работы функции с информацией об акциях")
    finnhub_client = finnhub.Client(api_key=os.getenv("API_KEY_FINNHUB"))

    stock_prices = []
    currency_stocks_logger.info("Функция обрабатывает данные транзакций.")
    for ind in stocks:
        quote = finnhub_client.quote(ind)
        currency_stocks_logger.info("Формирование списка словарей с данными об акциях")
        stock_prices.append({"stock": ind, "price": quote["c"]})
    currency_stocks_logger.info("Конец работы функции с информацией об акциях")
    return stock_prices


# if __name__ == '__main__':
#     with open('../data/user_settings.json', 'r', encoding='utf-8') as file:
#         json_data = json.load(file)
#     values_stocks_to_request = (json_data ["user_stocks"])
#     print(currency_stocks(values_stocks_to_request))
