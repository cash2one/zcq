#!/usr/bin/env python3
#-*- encoding: utf-8 -*-

"""Encrypt password using RSA
"""

import rsa

class RSAEncryption(object):
    """Enctyption class using rsa"""

    def __init__(self, N, E):
        """rsa_enc = RSAEncryption(N, E)
        where N is a big prime number and E stands for the exponent.
        """
        self.N = N
        self.E = E

        self.pubkey = rsa.key.PublicKey(N, E)

    def encrypt(self, message):
        """Encrypt the text message"""
        if isinstance(message, bytes):
            m = message
        elif isinstance(message, str):
            m = message.encode()
        else:
            raise ValueError("bytes or str object expected, got {}".format(type(message)))

        return rsa.encrypt(m, self.pubkey)



if __name__ == '__main__':
    pass

