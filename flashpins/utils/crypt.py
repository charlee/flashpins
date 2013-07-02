# -*- coding: utf8 -*-

import hashlib
from flashpins.utils import base62_encode

def urlhash(url):
    m = hashlib.sha1()
    m.update(url)

    h = m.hexdigest()[:9]

    return base62_encode(int(h, 16))

