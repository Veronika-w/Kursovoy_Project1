import json

import pandas as pd
import pytest

from src.reports import cost_by_category


@pytest.fixture
def transactions():
    return pd.DataFrame(
        {
            "Категория": ["Красота", "Транспорт", "Красота", "Транспорт", "Красота"],
            "Дата платежа": ["10.08.2020", "15.08.2020", "20.08.2020", "nan", "23.08.2020"],
            "Сумма платежа": [3500, 200, 5000, 3800, 3000],
        }
    )


def test_with_date_1(transactions):
    result = cost_by_category(transactions, category="Транспорт", date="15.08.2020")
    result_list = json.loads(result)

    assert result_list[0]["amount"] == 200


def test_with_date_2(transactions):
    result = cost_by_category(transactions, category="Красота", date="20.08.2020")
    result_list = json.loads(result)

    assert result_list[0]["amount"] == 3500
    assert result_list[1]["amount"] == 5000


def test_no_transactions_in_category(transactions):
    result = cost_by_category(transactions, category="Еда", date=None)
    result_list = json.loads(result)

    assert len(result_list) == 0
