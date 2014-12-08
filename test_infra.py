from unittest import TestCase
from infra import infra

__author__ = 'witlox'


class TestInfra(TestCase):
    def test_add(self):
        f = infra()
        self.assertEqual(3, f.add(1,2))

