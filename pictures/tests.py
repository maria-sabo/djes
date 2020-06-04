from django.test import TestCase

import unittest
import json


class MyFuncTestCase(unittest.TestCase):
    def testBasic(self):
        a = ['larry', 'curly', 'moe']
        self.assertEqual(my_func(a, 0), 'larry')
        self.assertEqual(my_func(a, 1), 'curly')

    def testBasic2(self):
        a = ['larry', 'curly', 'moe']
        self.assertEqual(1, 1)
        self.assertEqual(my_func(a, 1), 'curly')


def my_func(a_list, idx):
    return a_list[idx]
