import unittest

from darklight.aux.whirlpool import Whirlpool

class WhirlpoolTest(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(Whirlpool("").hexdigest(),
            "19fa61d75522a4669b44e39c1d2e1726c530232130d407f89afee0964997f7a7"
            "3e83be698b288febcf88e3e03c4f0757ea8964e59b63d93708b138cc42a66eb3")

    def test_quick_fox(self):
        self.assertEqual(
            Whirlpool("The quick brown fox jumps over the lazy dog").hexdigest(),
            "b97de512e91e3828b40d2b0fdce9ceb3c4a71f9bea8d88e75c4fa854df36725f"
            "d2b52eb6544edcacd6f8beddfea403cb55ae31f03ad62a5ef54e42ee82c3fb35")

    def test_lazy_eog(self):
        self.assertEqual(
            Whirlpool("The quick brown fox jumps over the lazy eog").hexdigest(),
            "c27ba124205f72e6847f3e19834f925cc666d0974167af915bb462420ed40cc5"
            "0900d85a1f923219d832357750492d5c143011a76988344c2635e69d06f2d38c")
