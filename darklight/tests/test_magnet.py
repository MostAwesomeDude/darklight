import unittest

from darklight.magnet import parse_magnet, parse_urn

class ParseURNTest(unittest.TestCase):

    def test_simple(self):
        namespace, data = parse_urn("urn:namespace:data")
        self.assertEqual(namespace, "namespace")
        self.assertEqual(data, "data")

    def test_complex_namespace(self):
        namespace, data = parse_urn("urn:tree:tiger:ASDF")
        self.assertEqual(namespace, "tree:tiger")
        self.assertEqual(data, "ASDF")

    def test_invalid_header(self):
        self.assertRaises(Exception, parse_urn, "hurp:derp:hurpaderp")

class ParseMagnetTest(unittest.TestCase):

    def test_size(self):
        d = parse_magnet("magnet:?xl=1")
        self.assertEqual(d["size"], 1)

    def test_invalid_header(self):
        self.assertRaises(Exception, parse_magnet, "hurp:?xt=1234")

    def test_base32_padded(self):
        magnet = ("magnet:"
            "?xt=urn:tree:tiger:4ZSRNBDNLLOHAJJ75ZMKONCCFD4EPUOWUEZDEYI=")
        d = parse_magnet(magnet)
        self.assertEqual(d["xt"],
            "\xe6e\x16\x84mZ\xdcp%?\xeeX\xa74B(\xf8G\xd1\xd6\xa122a")
