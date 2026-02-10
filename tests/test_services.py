import json

import pytest

from src.services import cashback_categories


@pytest.fixture
def cashback():
    return [
        {"Дата платежа": "01.08.2020", "Сумма платежа": -45.0, "Категория": "Супермаркеты"},
        {"Дата платежа": "11.08.2020", "Сумма платежа": -69.99, "Категория": "Супермаркеты"},
        {"Дата платежа": "21.08.2020", "Сумма платежа": -110.0, "Категория": "Транспорт"},
        {"Дата платежа": "28.08.2020", "Сумма платежа": -491.0, "Категория": "Супермаркеты"},
        {"Дата платежа": "30.08.2020", "Сумма платежа": -5800.0, "Категория": "Перевод"},
    ]


def test_cashback_categories(cashback):

    expected = json.dumps({"Перевод": 58.0, "Супермаркеты": 4.0, "Транспорт": 1.0}, ensure_ascii=False)
    result = cashback_categories(cashback, 2020, 8)
    assert result == expected
