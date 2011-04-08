import StringIO
import unittest

from darklight.core.conf import DarkConf

testconf = StringIO.StringIO("""
# Comment one
; Comment two

[cache]
size = 1000
hash_style = immediate
[database]
path = test.db
[ssl]
enabled = True
key = test.key
certificate = test.crt
""")

class TestDarkConf(unittest.TestCase):

    def setUp(self):
        self.dc = DarkConf()

    def test_conf(self):
        self.dc.readfp(testconf)
        self.assertEqual(self.dc.getint("cache", "size"), 1000)
        self.assertEqual(self.dc.get("cache", "hash_style"),
            "immediate")

        self.assertEqual(self.dc.get("database", "path"), "test.db")

        self.assertTrue(self.dc.getboolean("ssl", "enabled"))
        self.assertEqual(self.dc.get("ssl", "key"), "test.key")
        self.assertEqual(self.dc.get("ssl", "certificate"), "test.crt")

if __name__ == "__main__":
    unittest.main()
