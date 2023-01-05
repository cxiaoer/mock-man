import unittest

from request import RequestItem
from tools import json_equals, get_cls_props


class TestTools(unittest.TestCase):
    def test_json_equals(self):
        j1 = '[{"name":"张三"},{"name1":"李四"}]'
        j2 = '[{"name1":"李四"},{"name":"张三"}]'
        self.assertTrue(json_equals(j2, j1))

    def test_get_fields(self):
        a = RequestItem()
        print(a.__doc__)
        for attribute, value in a.__dict__.items():
            print(attribute, value)
        print(RequestItem.__dict__.keys())

    def test_get_cls_props(self, cls_props=get_cls_props(RequestItem)):
        props = cls_props
        print(props)
        a = RequestItem()
        a.url_path = 'hello'
        print(a.__getattribute__(props[0]))
        self.assertTrue(a.__getattribute__(props[0]) == 'hello')
