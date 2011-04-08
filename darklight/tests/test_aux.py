import base64
import hashlib
import random
import unittest

import darklight.aux

class WhirlpoolTest(unittest.TestCase):

    def test_builtin(self):
        strings = "", "The quick brown fox jumps over the lazy dog."
        for string in strings:
            self.assertEqual(hashlib.new("whirlpool", string).digest(),
                darklight.aux.Whirlpool(string).digest())


class HMACTest(unittest.TestCase):

    def test_simple(self):
        darklight.aux.DarkHMAC("")

    def test_builtin(self):
        darklight.aux.use_builtin_whirlpool = False
        default = darklight.aux.DarkHMAC("test")

        darklight.aux.use_builtin_whirlpool = True
        other = darklight.aux.DarkHMAC("test")

        self.assertEqual(default, other)

class UtilTest(unittest.TestCase):

    def setUp(self):
        import darklight.aux.util

    def test_trivial(self):
        pass

    def test_base32(self):
        for i in range(100):
            s = "".join(chr(random.randint(0, 255)) for x in range(i))
            self.assertEqual(s,
                darklight.aux.util.deserialize(base64.b32encode(s), len(s)))

if __name__ == "__main__":
    unittest.main()
