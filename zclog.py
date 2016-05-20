#!/usr/bin/env python

import logging

logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S')

def getLogger(name='', level=logging.DEBUG):
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(console)
    return logger


if __name__ == '__main__':
    pass

