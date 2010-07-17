import unittest

import darklight.aux

class HMACTest(unittest.TestCase):

    def test_simple(self):
        darklight.aux.DarkHMAC("")

    def test_builtin(self):
        darklight.aux.use_builtin_whirlpool = False
        default = darklight.aux.DarkHMAC("test")

        darklight.aux.use_builtin_whirlpool = True
        other = darklight.aux.DarkHMAC("test")

        self.assertEqual(default, other)

if __name__ == "__main__":
    unittest.main()
