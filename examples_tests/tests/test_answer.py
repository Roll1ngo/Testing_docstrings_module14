import unittest
from unittest.mock import patch

from examples_tests.src.reduce_sum.answer import numbers, sum_numbers
import examples_tests.src.reduce_sum.answer


class TestClass(unittest.TestCase):
    # @patch('examples_tests.src.reduce_sum.answer.other')
    # def test_result(self, mock_other):
    #     result = sum_numbers(numbers)
    #     self.assertEqual(result, 96)
    #     mock_other.assert_called()

    @patch('src.reduce_sum.answer.other')
    def test_result_reduce(self, mock_other):
        with patch.object(examples_tests.src.reduce_sum.answer, 'reduce') as mock_reduce:
            mock_reduce.return_value = 196
            result = sum_numbers(numbers)
            self.assertEqual(result, 196)
            mock_other.assert_called()
