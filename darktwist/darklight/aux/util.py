import base64
import binascii

def deserialize(string, length):
    """
    Given a string and its expected length, try a variety of encodings to get
    it back into its original format.

    Expected input formats include base64/base32 and binascii. The idea is to
    go from wire-safe/readable formats to raw bytes.
    """

    if len(string) == length:
        return string
    elif len(string) == length * 2:
        # Hexlified
        return binascii.unhexlify(string)
    elif abs(len(string) / 8 - length / 6) <= 1:
        return base64.b64decode(string)
    elif abs(len(string) / 8 - length / 5) <= 1:
        return base64.b32decode(string)
    else:
        raise ValueError, "Couldn't guess how to deserialize %s" % string
