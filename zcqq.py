#!/usr/bin/env python3
#-*- encoding: utf-8 -*-

import os
import sys
import argparse
from pyzcqq import QQReg

parser = argparse.ArgumentParser(description='QQ register configuration.')
parser.add_argument('-r', '--random', type=int,
                   help='set non-zero to randonly generate nicks, passwords, birthdays, areas etc.')
parser.add_argument('-c', '--captcha', type=str,
                   help='where to get captcha, reasonable values are: console, ruokuai')
parser.add_argument('-p', '--phone', type=str,
                   help='where to get phone numbers, reasonable values are: console, remote')
parser.add_argument('-ru', '--ruokuai-user', dest='rk_user', type=str,
                   help='if use `-c ruokuai`, this option specifies ruokuai username')
parser.add_argument('-rp', '--ruokuai-password', dest='rk_pass', type=str,
                   help='if use `-c ruokuai`, this option specifies ruokuai username')
                   

# parser.add_argument('--sum', dest='accumulate', action='store_const',
                   # const=sum, default=max,
                   # help='sum the integers (default: find the max)')


args = parser.parse_args()

qqreg = QQReg(
            random=args.random, 
            captcha=args.captcha, 
            phone=args.phone, 
            rk_user=args.rk_user, 
            rk_pass=args.rk_pass
        )
qqreg.do_reg()

if __name__ == '__main__':
    pass
    
