import unittest

from frozen_json import FrozenJSON


class TestFrozenJSON(unittest.TestCase):

    def test_frozen(self):
        o = [{
            "hello": "world"
        }]
        f = FrozenJSON(o)
        self.assertTrue(f[0].hello == 'world')
