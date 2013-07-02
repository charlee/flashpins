# -*- coding: utf8 -*-

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def base62_encode(num):
    return baseconvert(num, ALPHABET)

def baseconvert(num, symbols):

    base = len(symbols)
    digits = []

    while num:
        r = num % base
        num = num // base
        digits.append(symbols[r])
    digits.reverse()

    return ''.join(digits)

