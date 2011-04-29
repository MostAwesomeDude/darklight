"""
Magnet link parser and assembler.

This parser only handles the parts of magnet links relevant to Darklight.
"""

from base64 import b32decode, b32encode

def parse_urn(urn):
    """
    Parse a URN.
    """

    if urn[:4] != "urn:":
        raise Exception("Invalid URN %r" % urn)

    urn = urn[4:]
    namespace, colon, data = urn.rpartition(":")
    return namespace, data

def parse_magnet(uri):
    """
    Parse a magnet link.

    Returns a dict with the various parameters in the URI.
    """

    magic, parameters = uri.split("?")

    if magic != "magnet:":
        raise Exception("Invalid magnet link %r" % uri)

    d = {}
    for parameter in parameters.split("&"):
        key, value = parameter.split("=", 1)

        if key == "xl":
            d["xl"] = int(value)
            d["size"] = d["xl"]
        elif key == "xt":
            namespace, data = parse_urn(value)
            if namespace == "tree:tiger":
                d["xt"] = b32decode(data)
                d["hash"] = d["xt"]

    return d

def create_magnet(size, h):
    """
    Create a magnet link for a given node in a TTH.
    """

    uri = "magnet:?xl=%d&xt=urn:tree:tiger:%s" % (size, b32encode(h))
    return uri
