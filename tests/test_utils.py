import os
from datetime import datetime
from unittest.mock import Mock, mock_open, patch

import pandas as pd
import pytest
from dotenv import load_dotenv

from src.utils import (currency_rate, currency_stocks, filter_by_date, get_user_settings, greetings, operations_card,
                       read_excel_file, top_five_transactions)

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_KEY_FINNHUB = os.getenv("API_KEY_FINNHUB")


@pytest.fixture
def sample_data():
    """Создает список данных для тестов."""
    return [
        {
            "Дата платежа": "01.08.2020",
            "Статус": "OK",
            "Сумма платежа": -47.0,
            "Валюта платежа": "RUB",
            "Категория": "Супермаркеты",
            "Описание": "Магнит",
            "MCC": 5411,
            "Номер карты": "*7197",
        },
        {
            "Дата платежа": "05.08.2020",
            "Статус": "OK",
            "Сумма платежа": -45.0,
            "Валюта платежа": "RUB",
            "Категория": "Супермаркеты",
            "Описание": "Колхоз",
            "MCC": 5499,
            "Номер карты": "*7197",
        },
        {
            "Дата платежа": "25.08.2020",
            "Статус": "OK",
            "Сумма платежа": -130.0,
            "Валюта платежа": "RUB",
            "Категория": "Фастфуд",
            "Описание": "Kofe s sobojj",
            "MCC": 5814,
            "Номер карты": "*7197",
        },
    ]


@pytest.fixture
def mock_data():
    """Создает фиктивные данные для тестирования."""
    return [
        {"Дата платежа": "01.09.2021", "Сумма платежа": 5990.0, "Категория": "Каршеринг", "Описание": "Ситидрайв"},
        {
            "Дата платежа": "20.05.2021",
            "Сумма платежа": 8626.0,
            "Категория": "Бонусы",
            "Описание": "Компенсация покупки",
        },
        {"Дата платежа": "14.05.2019", "Сумма платежа": 42965.94, "Категория": "Другое", "Описание": "ГУП ВЦКП ЖХ"},
        {
            "Дата платежа": "30.04.2019",
            "Сумма платежа": 6100.0,
            "Категория": "Зарплата",
            "Описание": 'Пополнение. ООО "ФОРТУНА". Зарплата',
        },
        {
            "Дата платежа": "23.04.2019",
            "Сумма платежа": 4518.0,
            "Категория": "Сервис",
            "Описание": "Kopirovalniy Centr",
        },
        {
            "Дата платежа": "15.04.2019",
            "Сумма платежа": 6000.0,
            "Категория": "Зарплата",
            "Описание": 'Пополнение. ООО "ФОРТУНА". Аванс',
        },
        {
            "Дата платежа": "21.03.2019",
            "Сумма платежа": 190044.51,
            "Категория": "Переводы",
            "Описание": "Перевод Кредитная карта. ТП 10.2 RUR",
        },
        {
            "Дата платежа": "28.08.2018",
            "Сумма платежа": 32999.0,
            "Категория": "Различные товары",
            "Описание": "SPb Trk Atmosfera",
        },
    ]


@pytest.fixture
def report():
    return [
        {"Дата платежа": "01.09.2021", "Сумма платежа": -2000.0, "Категория": "Супермаркеты"},
        {"Дата платежа": "10.09.2021", "Сумма платежа": -300.0, "Категория": "Фастфуд"},
        {
            "Дата платежа": "14.09.2021",
            "Сумма платежа": 525.0,
            "Категория": "Бонусы",
        },
        {"Дата платежа": "16.09.2021", "Сумма платежа": -400.0, "Категория": "Супермаркеты"},
        {"Дата платежа": "03.10.2021", "Сумма платежа": -1100.0, "Категория": "Переводы"},
        {
            "Дата платежа": "23.10.2021",
            "Сумма платежа": -800.0,
            "Категория": "Супермаркеты",
        },
        {
            "Дата платежа": "25.10.2021",
            "Сумма платежа": 525.0,
            "Категория": "Бонусы",
        },
        {"Дата платежа": "05.11.2021", "Сумма платежа": -400.0, "Категория": "Супермаркеты"},
        {"Дата платежа": "05.11.2021", "Сумма платежа": -1100.0, "Категория": "Переводы"},
        {
            "Дата платежа": "14.11.2021",
            "Сумма платежа": -800.0,
            "Категория": "Супермаркеты",
        },
        {
            "Дата платежа": "14.12.2021",
            "Сумма платежа": 525.0,
            "Категория": "Бонусы",
        },
        {"Дата платежа": "18.12.2021", "Сумма платежа": -400.0, "Категория": "Супермаркеты"},
    ]


test_cases = [
    (datetime(2020, 8, 25, 6, 0), "Доброе утро!"),
    (datetime(2020, 7, 12, 15, 0), "Добрый день!"),
    (datetime(2020, 10, 13, 20, 0), "Добрый вечер!"),
    (datetime(2020, 12, 5, 22, 30), "Добрый вечер!"),
    (datetime(2020, 11, 8, 5, 0), "Доброй ночи!"),
]


@pytest.mark.parametrize("date_now, expected_greeting", test_cases)
def test_greetings(date_now, expected_greeting):
    """Тестирование функции вывода приветствия в зависимости от времени суток"""
    assert greetings(date_now) == expected_greeting


@pytest.mark.parametrize(
    "input_date, expected",
    [
        (
            "2020-08-25",
            [
                {
                    "Дата платежа": "01.08.2020",
                    "Статус": "OK",
                    "Сумма платежа": -47.0,
                    "Валюта платежа": "RUB",
                    "Категория": "Супермаркеты",
                    "Описание": "Магнит",
                    "MCC": 5411,
                    "Номер карты": "*7197",
                },
                {
                    "Дата платежа": "05.08.2020",
                    "Статус": "OK",
                    "Сумма платежа": -45.0,
                    "Валюта платежа": "RUB",
                    "Категория": "Супермаркеты",
                    "Описание": "Колхоз",
                    "MCC": 5499,
                    "Номер карты": "*7197",
                },
                {
                    "Дата платежа": "25.08.2020",
                    "Статус": "OK",
                    "Сумма платежа": -130.0,
                    "Валюта платежа": "RUB",
                    "Категория": "Фастфуд",
                    "Описание": "Kofe s sobojj",
                    "MCC": 5814,
                    "Номер карты": "*7197",
                },
            ],
        ),
        ("", []),
        ("2021-12-03", []),
        (
            "2020-08-01",
            [
                {
                    "Дата платежа": "01.08.2020",
                    "Статус": "OK",
                    "Сумма платежа": -47.0,
                    "Валюта платежа": "RUB",
                    "Категория": "Супермаркеты",
                    "Описание": "Магнит",
                    "MCC": 5411,
                    "Номер карты": "*7197",
                }
            ],
        ),
    ],
)
def test_filter_by_date(input_date, expected, sample_data):
    """Тестирование функции фильтрации данных по заданной дате"""
    result = filter_by_date(input_date, sample_data)
    assert result == expected


@patch("pandas.read_excel")
def test_read_excel_file(mock_read_excel, sample_data):
    """Тестирование функции чтения из Excel файла"""
    mock_read_excel.return_value = pd.DataFrame(sample_data)
    result = read_excel_file("mock_file.xlsx")
    expected = [
        {
            "Дата платежа": "01.08.2020",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма платежа": -47.0,
            "Валюта платежа": "RUB",
            "Категория": "Супермаркеты",
            "MCC": 5411,
            "Описание": "Магнит",
        },
        {
            "Дата платежа": "05.08.2020",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма платежа": -45.0,
            "Валюта платежа": "RUB",
            "Категория": "Супермаркеты",
            "MCC": 5499,
            "Описание": "Колхоз",
        },
        {
            "Дата платежа": "25.08.2020",
            "Статус": "OK",
            "Сумма платежа": -130.0,
            "Валюта платежа": "RUB",
            "Категория": "Фастфуд",
            "Описание": "Kofe s sobojj",
            "MCC": 5814,
            "Номер карты": "*7197",
        },
    ]
    assert result == expected
    mock_read_excel.assert_called_once_with("mock_file.xlsx")


@patch("pandas.read_excel")
def test_read_excel_file_file_not_found(mock_read_excel):
    """Тестирование чтения Excel файла, если файл не найден"""
    mock_read_excel.side_effect = FileNotFoundError
    result = read_excel_file("non_existing_file.xlsx")
    assert result == []


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            [
                {"Номер карты": "*4556", "Сумма платежа": -545.0},
                {"Номер карты": "*4556", "Сумма платежа": -200.0},
                {"Номер карты": "*7197", "Сумма платежа": -1050.0},
            ],
            [
                {"last_digits": "4556", "total_spent": 745.0, "cashback": 7.45},
                {"last_digits": "7197", "total_spent": 1050.0, "cashback": 10.50},
            ],
        ),
        ([], []),
        (
            [
                {"Номер карты": "nan", "Сумма платежа": "nan"},
                {"Номер карты": float("nan"), "Сумма платежа": float("nan")},
            ],
            [],
        ),
    ],
)
def test_operations_card(input_data, expected):
    """Тестирование функции, возвращающей данные по карте"""
    result = operations_card(input_data)
    assert result == expected


def test_top_five_transactions(mock_data):
    """Тестирование функции, возвращающей топ-5 транзакций"""
    result = top_five_transactions(mock_data)

    expected = [
        {
            "date": "21.03.2019",
            "amount": 190044.51,
            "category": "Переводы",
            "description": "Перевод Кредитная карта. ТП 10.2 RUR",
        },
        {"date": "14.05.2019", "amount": 42965.94, "category": "Другое", "description": "ГУП ВЦКП ЖХ"},
        {"date": "28.08.2018", "amount": 32999.0, "category": "Различные товары", "description": "SPb Trk Atmosfera"},
        {"date": "20.05.2021", "amount": 8626.0, "category": "Бонусы", "description": "Компенсация покупки"},
        {
            "date": "30.04.2019",
            "amount": 6100.0,
            "category": "Зарплата",
            "description": 'Пополнение. ООО "ФОРТУНА". Зарплата',
        },
    ]
    assert result == expected


@pytest.mark.parametrize(
    "input_data, expected",
    [
        ([], []),
        (
            [
                {
                    "Дата платежа": "01.01.2023",
                    "Сумма платежа": 150,
                    "Категория": "Пополнения",
                    "Описание": "Пополнение",
                },
                {
                    "Дата платежа": "02.01.2023",
                    "Сумма платежа": 200,
                    "Категория": "Пополнения",
                    "Описание": "Пополнение",
                },
            ],
            [],
        ),
    ],
)
def test_transaction_rating_by_amount(input_data, expected):
    """Тестирование функции, возвращающей рейтинг транзакций по сумме"""
    result = top_five_transactions(input_data)
    assert result == expected


# @pytest.fixture
# def trans_1():
#     return ["USD", "EUR"]
#
#
# @patch('requests.get')
# def test_currency_conversion(mock_get, trans_1):
#     """Тестирование функции вывода курса валют"""
#     mock_get.return_value.json.return_value = [
#             {"currency": "USD", "rate": 99.82},
#             {"currency": "EUR", "rate": 103.83}
#         ]
#     assert currency_rate(trans_1) == [
#             {"currency": "USD", "rate": 99.82},
#             {"currency": "EUR", "rate": 103.83}
#         ]

#
# def test_exchange_rate_no_currencies():
#     """Тестирование, если передан пустой список"""
#     result = currency_rate([])
#     assert result == []


# @patch('requests.get')
# def test_get_price_stock(mock_get):
#     """Тестирование функции получения данных об акциях"""
#     mock_response = Mock()
#     mock_response.json.return_value = {
#         "Global Quote": {"05. price": "150.25"}
#     }
#     mock_get.return_value = mock_response
#     stocks = {"AAPL", "MSFT"}
#     expected_result = [{'price': 278.66, 'stock': 'AAPL'}, {'price': 395.52, 'stock': 'MSFT'}]
#
#     result = currency_stocks(stocks)
#     assert result == expected_result


def test_get_price_stock_empty_list():
    """Тестирование, если передан пустой словарь"""
    result = currency_stocks({})
    expected = []
    assert result == expected


# @patch('requests.get')
# def test_get_price_stock_invalid_response(mock_get):
#     mock_response = Mock()
#     mock_response.json.return_value = {
#         "Global Quote": {"05. price": "invalid_price"}
#     }
#     mock_get.return_value = mock_response
#     stocks = {"GOOGL"}
#     with pytest.raises(ValueError):
#         currency_stocks(stocks)


@pytest.mark.parametrize(
    "mock_data, expected",
    [
        ('[{"currency": "USD"}, {"stock": "AAPL"}]', [{"currency": "USD"}, {"stock": "AAPL"}]),  # Успешное чтение
        (None, []),
        ('{"currency": "USD", "stock": AAPL}', []),
    ],
)
def test_get_user_settings(mock_data, expected):
    if mock_data is None:  # Обработка случая FileNotFoundError
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = get_user_settings("dummy_path.json")
            assert result == expected
    else:
        with patch("builtins.open", new_callable=mock_open, read_data=mock_data):
            result = get_user_settings("dummy_path.json")
            assert result == expected
