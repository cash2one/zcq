#!/usr/bin/env python3
#-*- encoding: utf-8 -*-

import os
import sys
import json
import base64
import hashlib
import logging
import subprocess
import urllib.parse
import urllib.request
import http.cookiejar

SERVER = 'http://192.168.4.194:8088'

FORMAT = '[%(asctime)-15s] %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

class LoginFailException(Exception): pass
class NoPhoneException(Exception): pass

class RegClient(object):
    '''Registeration client
    '''
    
    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.cookies = http.cookiejar.CookieJar()
        self.session = ''
        
        self.login_count = 0
        self.login_auth = ''
        self.phone_cache_filename = 'avaiphones.txt'
        
    def login(self):
        self.login_count += 1
        url = '{}/1/{}/4?p={}'.format(SERVER, self.name, urllib.parse.quote(self.login_auth))
        logging.info('request pass: %s', self.login_auth)
        
        if self.login_count > 2:
            self.login_count = 0
            raise LoginFailException('Login has been tried too many times')
        
        cookieprocessor = urllib.request.HTTPCookieProcessor(self.cookies)
        self.opener = urllib.request.build_opener(cookieprocessor)
        req = urllib.request.Request(url)
        res = self.opener.open(req)
        
        con = res.read()
        con = con.decode()
        logging.info('response: %s', con)
        if con == 'ok':
            # login success
            logging.info('login success')
            self.cookies.extract_cookies(res, req)
            for ck in self.cookies:
                logging.info('cookie: %s=%s', ck.name, ck.value)
                if ck.name == 's':
                    self.session = ck.value
                    break
            logging.info('session: %s', self.session)
        elif con == 'need authorization':
            # auth
            logging.info('Cookie: %s', res.getheader('Set-Cookie'))
            self.cookies.extract_cookies(res, req)
            n = None
            for ck in self.cookies:
                logging.info('cookie: %s=%s', ck.name, ck.value)
                if ck.name == 'n':
                    n = ck.value
                    break
            b = '{}-{}'.format(n, self.password).encode()
            m = hashlib.md5(b)
            self.login_auth = base64.b64encode(m.digest()).decode()
            return self.login()
        elif con == 'authorized failure':
            # fail
            return False
            
        return True
        
    
    def get_session(self):
        return self.session
        
     
    def get_phones(self):
        url = '{}/1/{}/5'.format(SERVER, self.name)
        
        res = self.opener.open(url)
        con = res.read()
        with open(self.phone_cache_filename , 'wb') as f:
            f.write(con)
        con = con.decode()
        logging.info('response: %s', con)
        self.available_phones = json.loads(con)
        logging.info('phones: %s',  self.available_phones)
        return True
        
    
    def start_reg(self):

        # read from cache
        with open(self.phone_cache_filename, 'rb') as f:
            con = f.read()
        self.available_phones.extend(json.loads(con.decode()))

        if len(self.available_phones) == 0:
            raise  NoPhoneException('no avaiable phone numbers')
            
        if sys.platform == 'win32':
            py = 'py -3'
        else:
            py = 'python3'
            
        args = [py, 'zcqq.py', '-r', 1, '-c', 'ruokuai', '-p', 'remote']
            
        sb = subprocess.Popen(args)
        
        
    def __repr__(self):
        return 'RegClient(name={})'.format(self.name)
    

if __name__ == '__main__':
    rc = RegClient('m1', 'm1')
    try:
        ok = rc.login()
    except Exception as e:
        logging.error(e)
        sys.exit(0)
    else:
        logging.info('login ok')
        rc.get_phones()
    self.start_reg()
        

