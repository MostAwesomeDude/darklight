import tempfile
import unittest

import darklight.core

class TestDarkConf(unittest.TestCase):

    def setUp(self):
        self.dc = darklight.core.DarkConf()

    def test_trivial(self):
        pass

    def test_empty(self):
        with tempfile.NamedTemporaryFile() as tf:
            self.dc.parse(tf.name)
