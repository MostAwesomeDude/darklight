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

    def test_path(self):
        with tempfile.NamedTemporaryFile() as tf:
            path = "test.db"
            tf.write("DB %s" % path)
            tf.flush()
            self.dc.parse(tf.name)
            self.assertEqual(path, self.dc.path)

    def test_ssl(self):
        with tempfile.NamedTemporaryFile() as tf:
            tf.write("SSL test.key test.crt")
            tf.flush()
            self.dc.parse(tf.name)
            self.assertTrue(self.dc.ssl)
