import unittest
from unittest.mock import MagicMock
import asyncio

from examples_tests.src.example.ops import mul, div, add, sub

# some_string = "I am string"
# copy_str = some_string


# class TestMultiplication(unittest.TestCase):

# def test_multiply_two_positive_numbers(self):
#     result = mul(2, 3)
#     self.assertEqual(result, 6)
#
# def test_multiply_positive_and_negative_numbers(self):
#     result = mul(-1, -5)
#     self.assertTrue(result, "Why?")
#
# def test_multiply_two_negative_numbers(self):
#     result = mul(-2, -5)
#     self.assertEqual(result, 10)
#
# def test_strings(self):
#     self.assertIs(copy_str, "I am string")
#
# def test_return_none(self):
#     self.assertIsNone(sub(8, 7))
#
# def test_raise_value_error(self):
#     self.assertRaises(ValueError, sub, a=7, b=8)


# class MyTest(unittest.TestCase):
#     def setUp(self):
#         self.my_list = [1, 2, 3]
#
#     def tearDown(self):
#         del self.my_list
#
#     def test_list_length(self):
#         self.my_list.append(4)
#         self.assertEqual(len(self.my_list), 4)
#
#     def test_list_contents(self):
#         self.assertListEqual(self.my_list, [1, 2, 3])


# class TestExamples(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         print('Start before all test')

# @classmethod
# def tearDownClass(cls):
#     print('Start after all test')
#
# def setUp(self):
#     a = 1

# def tearDown(self):
#     a = None
#
# def test_add(self):
#     print("Add function test")
#     self.assertEqual(add(2, 3), 5)
#
# def test_sub(self):
#     print("Sub function test")
#     self.assertRaises(ValueError, sub, 5, 6)
#
# def test_mul(self):
#     print("Mul function test")
#     self.assertEqual(mul(2, 3), 6)
#
# def test_div(self):
#     print("Div function test")
#     self.assertAlmostEqual(div(2, 3), 0.66666666)
#     with self.assertRaises(ZeroDivisionError) as cm:
#         div(3, 0)


# async def async_add(a, b):
#     await asyncio.sleep(1)
#     return a + b
#
#
# class TestAsyncMethod(unittest.IsolatedAsyncioTestCase):
#     async def test_add(self):
#         """Add function test"""
#         r = await async_add(2, 3)
#         self.assertEqual(r, 5)


class ProductionClass:
    apples = 12

    def return_number(self, a, b, c):
        total = self.apples + a + b + c
        return total


thing = ProductionClass()
thing.return_number = MagicMock(return_value=3)
thing.return_number(1, 2, 3, key='value')

thing.return_number.assert_called_with(1, 2, 3, key='value')

if __name__ == '__main__':
    unittest.main()
