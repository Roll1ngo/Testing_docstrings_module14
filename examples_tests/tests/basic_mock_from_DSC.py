import unittest
from unittest import TestCase, mock
import requests


def get_data_from_api():
    response = requests.get('https://api.example.com/data')
    return response.json()


class TestGetDataFromApi(TestCase):

    @mock.patch('requests.get')
    def test_get_data_from_api_success(self, mock_get):
        mock_response = mock.Mock()
        mock_response.json.return_value = {'key': 'value'}
        mock_get.return_value = {'key': 'value'}

        result = get_data_from_api()

        self.assertEqual(result, {'key': 'value'})
        mock_get.assert_called_once_with('https://api.example.com/data')

    @mock.patch('requests.get')
    def test_get_data_from_api_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException('API Error')

        with self.assertRaises(requests.exceptions.RequestException):
            get_data_from_api()

        mock_get.assert_called_once_with('https://api.example.com/data')


if __name__ == '__main__':
    unittest.main()
