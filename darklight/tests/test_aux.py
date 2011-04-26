import base64
import hashlib
import random
import unittest

from darklight.aux.hash import DarkHMAC
from darklight.aux.util import deserialize

class WhirlpoolTest(unittest.TestCase):

    def test_builtin(self):
        strings = "", "The quick brown fox jumps over the lazy dog."
        for string in strings:
            self.assertEqual(hashlib.new("whirlpool", string).digest(),
                darklight.aux.Whirlpool(string).digest())


class HMACTest(unittest.TestCase):

    def test_simple(self):
        DarkHMAC("")

    def test_builtin(self):
        use_builtin_whirlpool = False
        default = DarkHMAC("test")

        use_builtin_whirlpool = True
        other = DarkHMAC("test")

        self.assertEqual(default, other)

class UtilTest(unittest.TestCase):

    def test_base32(self):
        for i in range(100):
            s = "".join(chr(random.randint(0, 255)) for x in range(i))
            self.assertEqual(s, deserialize(base64.b32encode(s), len(s)))
