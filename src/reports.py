import datetime
import json
import logging
from typing import Any, Optional

import pandas as pd

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
    filename="../logs/reports.log",
    filemode="w",
)

cost_by_category_logger = logging.getLogger()


def decorator_cost_by_category(func: Any) -> Any:
    """Логирует результат функции в файл по умолчанию cost_by_category.json"""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        try:
            with open("cost_by_category.json", "w", encoding="utf-8") as f:
                cost_by_category.info("Запись отчёта в файл")
                json.dump(result, f, ensure_ascii=False, indent=4)
        except Exception as e:
            cost_by_category_logger.error(f"Произошла ошибка при записи в файл: {e}")
        return result

    return wrapper


@decorator_cost_by_category
def cost_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> Any:
    """Функция возвращающая траты за последние 3 месяца по заданной категории"""

    final_list = []

    if date is None:
        date_start = datetime.datetime.now() - datetime.timedelta(days=90)
    else:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        date_start = date_obj - datetime.timedelta(days=90)

    for index, transaction in transactions.iterrows():
        if transaction["Категория"] == category:

            if pd.isna(transaction["Дата платежа"]) or isinstance(transaction["Дата платежа"], float):
                continue
            try:
                transaction_date = datetime.datetime.strptime(str(transaction["Дата платежа"]), "%d.%m.%Y")
                if date_start <= transaction_date <= date_start + datetime.timedelta(days=90):
                    final_list.append({"date": transaction["Дата платежа"], "amount": transaction["Сумма платежа"]})
            except ValueError:
                continue

    return json.dumps(final_list, indent=4, ensure_ascii=False)
