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

    def test_comment(self):
        with tempfile.NamedTemporaryFile() as tf:
            tf.write("#")
            tf.flush()
            self.dc.parse(tf.name)

    def test_hashstyle(self):
        with tempfile.NamedTemporaryFile() as tf:
            tf.write("HASHSTYLE imm")
            tf.flush()
            self.dc.parse(tf.name)
            self.assertTrue(self.dc.immhash)
