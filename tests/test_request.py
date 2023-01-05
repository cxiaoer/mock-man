from unittest import TestCase
from request import RequestItem


class TestRequestItem(TestCase):
    def test_match_rules(self):
        item = RequestItem()
        self.assertTrue(not hasattr(item,'__match_rules'))
        self.assertTrue(hasattr(item, "url_path"))
