import os
from binascii import hexlify


def get_random_hash() -> str:
    return hexlify(os.urandom(10)).decode("utf-8")
