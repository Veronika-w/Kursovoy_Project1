import unittest
from unittest.mock import patch
from datetime import datetime
from src.utils import greeting

class TestGreeting(unittest.TestCase):

    @patch('src.utils.datetime')
    def test_evening_greeting(self, mock_datetime):
        mock_now = datetime(2023, 1, 1, 22, 0, 0)
        mock_datetime.now.return_value = mock_now

        mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)

        result = greeting()
        self.assertEqual(result, "Добрый вечер!")



@patch('request.get')
def test_currency_rate(mock_get):
    mock_get.return_value.json.return_value = "USD"
    assert currency_rate("1") == 1
    mock_get.assert_called_once_with(f"https://api.apilayer.com/exchangerates_data/latest?symbols=1")

if __name__ == '__main__':
    print(currency_rate(values_to_request))