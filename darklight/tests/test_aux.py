import base64
import random
import unittest

from darklight.aux.util import deserialize

class UtilTest(unittest.TestCase):

    def test_base32(self):
        for i in range(100):
            s = "".join(chr(random.randint(0, 255)) for x in range(i))
            self.assertEqual(s, deserialize(base64.b32encode(s), len(s)))
