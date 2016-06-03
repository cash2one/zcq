#!/usr/bin/env python3
#!-*- encoding: utf-8 -*-

'''QQ registration
'''

import os
import os.path
import time
import json
import string
import random
import logging
import urllib.parse
import urllib.request
import http.cookiejar
import rsa # third-party module
import encryption
import ruokuai

from devmain import find_regdev_by_session

GENDER_MALE = 1
GENDER_FEMALE = 2

# logging.basicConfig(level=logging.DEBUG,
                # format='%(asctime)s %(filename)s[line:%(lineno)d] [%(levelname)s] %(message)s',
                # datefmt='%Y-%m-%d %H:%M:%S')

class UnknownCaptchaFromException(Exception): pass
class PhonePoolEmptyException(Exception): pass

class PhonePool(object):
    '''Phone number pool'''
    def __init__(self, phone_list):
        self.phone_list = phone_list
        self.current_index = 0
        


    def first(self):
        if self.empty():
            raise PhonePoolEmptyException('phone pool is empty')
        self.curent_index = 0
        return self.phone_list[self.current_index]


    def next(self):
        if self.empty():
            raise PhonePoolEmptyException('phone pool is empty')

        try:
            phone = self.phone_list[self.current_index]
            self.current_index += 1
        except IndexError:
            self.current_index = -1
            phone = None
    
        return phone


    def empty(self):
        return self.phone_list is None or len(self.phone_list) == 0



class Cookie(object):
    """self defined cookie class"""
    
    def __init__(self, name, value, path="/", domain="", expires=""):
    
        self.name = name
        self.value = value
        self.path = path
        self.domain = domain
        self.expires = expires
        
    @staticmethod
    def fromstring(cookiestring):
        try:
            l = cookiestring.split(';')
        except Exception as e:
            return None
            
        try:
            name, value = l[0].strip().split('=')
            
        except Exception as e:
            return None
            
        try:
            n, path = l[1].strip().split('=')
            assert n.upper() == 'PATH'
        except Exception as e:
            path = '/'
            
        try:
            n, domain = l[2].strip().split('=')
            assert n.upper() == 'DOMAIN'
        except Exception as e:
            domain = ''
            
        try:
            n, expires = l[3].strip().split('=')
            assert n.upper() == 'EXPIRES'
        except Exception as e:
            expires = ''
            
        else:
            return Cookie(name, value, path, domain, expires)
        
    def __str__(self):
        return "{}={};".format(self.name, self.value)
        
    def __repr__(self):
        return "{}={}; PTH={}; DOMAIN={}; EXPIRES={}".format(self.name, self.value, self.path, self.domain, self.expires)

class QQReg(object):
    """QQ registration class"""
    
    name_set = string.digits + string.ascii_letters
    
    init_url    = "http://zc.qq.com/cgi-bin/cht/numreg/init?r={}"
    getacc_url  = "http://zc.qq.com/cgi-bin/cht/numreg/get_acc?r={}"
    monikey_url = "http://a.zc.qq.com/Cgi-bin/MoniKey?"
    captcha_url = "http://captcha.qq.com/getimage?aid=1007901&r={}"
    sendsms_url = "http://zc.qq.com/cgi-bin/cht/common/sms_send"
    referer_url = "http://zc.qq.com/cht/index.html"
    user_agent  = "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36"
    aq_input = {
            "nick": 1,
            "phone_num": 2,
            "self_email": 3,
            "other_email": 4,
            "password": 5,
            "password_again": 6,
            "sex_1": 7,
            "sex_2": 8,
            "birthday_type_value": 9,
            "year_value": 10,
            "month_value": 11,
            "day_value": 12,
            "country_value": 13,
            "province_value": 14,
            "city_value": 15,
            "code": 16
            }
    RSA_N = 0xC4D23C2DB0ECC904FE0CD0CBBCDC988C039D79E1BDA8ED4BFD4D43754EC9693460D15271AB43A59AD6D0F0EEE95424F70920F2C4A08DFDF03661300047CA3A6212E48204C1BE71A846E08DD2D9F1CBDDFF40CA00C10C62B1DD42486C70A09C454293BCA9ED4E7D6657E3F62076A14304943252A88EFA416770E0FBA270A141E7
    RSA_E = 0x10001

    def __init__(self, *args, **kwargs):
        """Iintialize a registration object.
        """
        self.if_rand        = kwargs.get('random', False)
        self.captcha_from   = kwargs.get('captcha', 'console')
        self.phone_from     = kwargs.get('phone', 'console')
        self.phone_list     = kwargs.get('phone_list', None)
        self.phone_pool     = PhonePool(self.phone_list)
        self.captcha_path   = kwargs.get('captcha_path', 'captcha')
        self.logfile        = kwargs.get('log_file', 'QQReg.log')
        self.rk_user        = kwargs.get('rk_user', None)
        self.rk_pass        = kwargs.get('rk_pass', None)
        self.server         = kwargs.get('server', None)
        self.dev_name       = kwargs.get('dev_name', None)
        self.dev_session    = kwargs.get('dev_session', None)
        
        # cookie
        self.cookies = http.cookiejar.CookieJar()
        
        # TODO: logger, different name and level
        self._logger = logging.getLogger("QQReg")
        self._logger.setLevel(logging.DEBUG)
        logging_handler = logging.FileHandler(self.logfile)
        formatter = logging.Formatter('%(asctime)s [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
        logging_handler.setFormatter(formatter)
        self._logger.addHandler(logging_handler)
        self.reg_dev = find_regdev_by_session(self.dev_session)

        if self.if_rand:
            self._init_rand()
            
        else:
            # TODO: initialize variables
            pass
            
        # other parameters
        self.elevel = 1
        self.phone = ''
        self.smsvc = ''
        self.need_reg = True
        self.goods = 0
        
        # directory to save captcha
        
        if not os.path.isdir(self.captcha_path):
            try:
                os.makedirs(self.captcha_path)
            except OSError as e:
                raise
        if not os.path.isdir("requst_cache"):
            try:
                os.makedirs("requst_cache")
            except OSError as e:
                raise
        
    def _init_rand(self):
        # name and password
        namelen = random.randint(8, 15)
        names = []
        for i in range(namelen):
            r = random.randrange(0, len(self.name_set))
            names.append(self.name_set[r])
        self.nickname = ''.join(names)
        self.password = self.nickname + '999'

        # rsa encryption
        rsa_inc = encryption.RSAEncryption(self.RSA_N, self.RSA_E)
        self.rsa_password = '{0:X}'.format(int.from_bytes(rsa_inc.encrypt(self.password), 'big'))
        self._logger.info('password: %s, rsa_password: %s', self.password, self.rsa_password)
        # gender
        self.gender = GENDER_MALE
        # country, province, city
        self.location = {}
        with open("city1.json", "rb") as f:
            con = f.read()
            self.location['1'] = location = json.loads(con.decode())
        self.country = '1' # China
        keys = list(location.keys())
        r1 = random.randrange(1, len(keys))
        k1 = keys[r1]
        if k1 == 'n':
            k1 = keys[r1-1]
        self.province = k1 # location[k1]['n']
        keys = list(location[k1].keys())
        r2 = random.randrange(1, len(keys))
        k2 = keys[r2]
        if k2 == 'n':
            k2 = keys[r2-1]
        self.city = k2 # location[k1][k2]['n']
        
        # year, month, day
        r = random.randint(18, 45)
        self.year = 2016 - r
        r = random.randint(1, 12)
        self.month = r
        r = random.randint(1, 28)
        self.day = r
        
    def _refresh_captha(self):
        
        
        headers = {
            "User-Agent": self.user_agent,
            "Referer": self.referer_url,
        }
        
        r = random.random()
        url = self.captcha_url.format(r)
        
        try:
            req = urllib.request.Request(url, None, headers)
            res = urllib.request.urlopen(req)
            cookie = res.getheader('Set-Cookie')
            
        except Exception as e:
            self._logger.error("Get captcha FAILED!")
            self._logger.critical(e)
            return False
            
        else:
            self._logger.info("Get captcha OK.")
            cookiestring = res.getheader('Set-Cookie')
            self._logger.debug("cookie: %s", cookiestring)
            #cookie = Cookie.fromstring(cookiestring)
            
            #self.cookies[cookie.name] = cookie.value
            self.cookies.extract_cookies(res, req)
            
            
            now = time.strftime("%Y%m%d-%H%M%S")
            self.captcha_name = os.path.join("captcha", "{}.jpg".format(now))
            self._logger.info("Save captcha to %s", self.captcha_name)
            
            with open(self.captcha_name, "wb") as f:
                f.write(res.read())
                
            return True
            
    def input_captcha(self):
        ok = self._refresh_captha()
        if not ok:
            return
        if self.captcha_from == 'console':
            # read captcha from console
            self.verifycode = input("Please input what you see in \"{}\":".format(self.captha_name))
            
        elif self.captcha_from == 'ruokuai':
            # use ruokuai
            if not self.rk_user:
                raise Exception('Ruokuai user is empty!')
            if not self.rk_pass:
                raise Exception('Ruokuai password is empty!')
            url = "http://api.ruokuai.com/create.json"
            paramKeys = ['username', 'password', 'typeid', 'timeout', 'softid', 'softkey']
            paramDict = {
                    'username': self.rk_user, 
                    'password': self.rk_pass,
                    'typeid': '3040',
                    'timeout': '100',
                    'softid': '57838',
                    'softkey': 'b61afeabc6d648c794354ceba073737c'
                    }
            with open(self.captcha_name, 'rb') as f:
                imagebytes = f.read()
            rk = ruokuai.APIClient()
            con = rk.http_upload_image(url, paramKeys, paramDict, imagebytes)
            obj = json.loads(con)
            self._logger.info('ruokuai returns: %s', con)
            self._logger.info('ruokuai returns verify code: %s', obj['Result'])
            self.verifycode = obj["Result"]
            self._rk_tid = obj['Id']
            
        else:
            raise UnknownCaptchaFromException("Unknown captcha source")

        self.__send_monikey("code", self.verifycode)

    def init_reg(self):
        self.start_time = time.strftime("%Y%m%d-%H%M%S")

        r = random.random()
        url = self.init_url.format(r)
        headers = {
                "User-Agent": self.user_agent,
                "Referer": self.referer_url,
                }
        try:
            self._logger.info('request for %s, headers: %s', url, headers)
            req = urllib.request.Request(url, None, headers)
            res = urllib.request.urlopen(req)
        except Exception as e:
            self._logger.error("try to init FAILED!!!")
            self._logger.critical(e)
        else:
            self._logger.info("init ok.")
            con = res.read()
            self._logger.info("response: %s", con.decode())
            cookiestring = res.getheader('Set-Cookie')
            self._logger.info("cookie: %s", cookiestring)
            # update cookie
            self.cookies.extract_cookies(res, req)


            init_result_file = os.path.join("requst_cache", "{}.res".format(self.start_time))
            with open(init_result_file, "ab+") as f:
                f.seek(0, 2)
                f.write(con)
                f.write(b'\n\n\n')

    def send_monikey_common(self):
        self.__send_monikey('nick', self.nickname)
        self.__send_monikey('password', self.password)
        self.__send_monikey('password_again', self.password)

    def __send_monikey(self, name, text):
    # TODO sleep for a while to send monikey request
        time.sleep(3)
        tm = '{0:.0f}'.format(time.time())
        tp = self.aq_input.get(name, 'year_value')
        query = '&'.join('{}|{}|{}'.format(ord(c), tp, tm) for c in text)
        headers = {
                "User-Agent": self.user_agent,
                "Referer": self.referer_url
                }
        try:
            url = self.monikey_url + query
            self._logger.info('requst %s', url)
            cookieprocessor = urllib.request.HTTPCookieProcessor(self.cookies)
            opener = urllib.request.build_opener(cookieprocessor)
            req = urllib.request.Request(url, None, headers)
            res = opener.open(req)
        except Exception as e:
            self._logger.critical(e)
        else:
            pass

    def input_phone(self):
        if not self.phone:
            self.phone = self.next_phone()
        if not self.phone:
            self._logger.info('phone number exhausted')
            self.need_reg = False
            return
        self.elevel = 3

        # send smsvc
        url = self.sendsms_url
        r = random.random()
        self._logger.info('use phone number %s to receive sms verify code.', self.phone)
        query = 'telphone={0}&elevel=3&regType=11&r={1}'.format(self.phone, r)
        headers = {
                "User-Agent": self.user_agent,
                "Referer": self.referer_url
                }
        try:
            dt = time.strftime('%Y%m%d-%H%M00')
            self._logger.info('requst %s?%s', url, query)
            cookieprocessor = urllib.request.HTTPCookieProcessor(self.cookies)
            opener = urllib.request.build_opener(cookieprocessor)
            req = urllib.request.Request(url, query.encode(), headers)
            res = opener.open(req)
        except Exception as e:
            self._logger.critical(e)
        else:
            self._logger.info('send sms responed!')
            con = res.read()
            con1 = con.decode()
            self._logger.info(con1)
            o = json.loads(con1)
            ec = o['ec']
            if ec == 0:
                # send sms ok
                self._logger.info('phone number ok, receive sms verify code')
                if self.phone_from == 'console' or self.phone == self.phone_from:
                    self.smsvc = input('Please input sms verify code: ')
                elif self.phone_from == 'carddrive':
                    # TODO use card drive to receive sms verify code
                    pass
                elif self.phone_from == 'remote':
                    # TODO use c/s mode to receive sms verify code
                    pass
                elif self.phone_from == 'local':
                    self._logger.info('need get sms verify code from %s', self.phone)
                elif self._check_phone(self.phone_from):
                    self._logger.info('use phone %s to receive sms', self.phone_from)
                    # TODO ask remote to receive sms verify code
                    if self.reg_dev is None:
                        self._logger.info('session %s is not binded to a client', self.dev_session)
                    else:
                        self.smsvc = self.regdev.get_smsvc(self.phone, dt)
            elif ec == 14:
                # already to limited number
                self._logger.info('this phone %s received up to limited sms.', self.phone)
                self.phone = '' # self.next_phone()
                #if not self.phone:
                #    self.need_reg = False
                #else:
                #    self._logger.info('change to use phone %s', self.phone)
                self.regdev.report_phone_sms_limited(self.phone)
            elif ec == 16:
                # TODO sms check error: what is this?
                pass
            elif ec == 4 or ec == 31:
                # phone format invalid
                self._logger.info('invalid phone: %s', self.phone)
                self.regdev.report_phone_invalid(self.phone)
            else:
                self._looger.info('error code: %d, will retry later', ec)

    
    def next_phone(self):
        phone = None
        if self.phone_from == 'console':
            phone = input('Please input phone number: ')
            phone = phone.strip()
            if not phone:
                return None
        elif self.phone_from == 'carddrive':
            # TODO Kucard implementation
            pass
        elif self.phone_from == 'remote':
            # TODO c/s mode phone number
            pass
        elif self.phone_from == 'local':
            # TODO get phone from local
            if self.phone_pool is None or self.phone_pool.empty():
                self._logger.error('phone from local, but pool is empty!')
                return 
            phone = self.phone_pool.next()

        else:
            if self._check_phone(self.phone_from):
                phone = self.phone_from
            else:
                self._logger.error('invalid phone: %s', self.phone_from)
                return 
        return phone

    def _check_phone(self, maybephone):
        maybephone = maybephone.strip()
        return (mybephone.startswith('1') 
                and len(maybephone) == 11 
                and maybephone.isnumeric())


    def do_reg(self):
        # TODO do actual regiter action
        while self.need_reg:
            self._reg()


    def _reg(self):

        if not self.phone and not self.smsvc:
            self.init_reg()
            self.send_monikey_common()
            self.input_captcha()

        query = self._format_query()

        r = random.random()
        url = self.getacc_url.format(r)
        headers = {
                "User-Agent": self.user_agent,
                "Referer": self.referer_url
                }

        try:
            self._logger.info('url: %s', url)
            self._logger.info('query: %s', query)
            self._logger.info('cookies: %s', self.cookies)
            cookieprocessor = urllib.request.HTTPCookieProcessor(self.cookies)
            opener = urllib.request.build_opener(cookieprocessor)
            req = urllib.request.Request(url, query.encode(), headers)
            res = opener.open(req)
        except Exception as e:
            self._logger.critical(e)
        else:
            self._logger.info("got getacc response")
            con = res.read()
            con1 = con.decode()
            self._logger.info(con1)
            o = json.loads(con1)
            filename = os.path.join('request_cache', self.start_time)

            with open(filename, "ab+") as f:
                f.write(b'getacc response: \n')
                f.write(con)
                f.write(b'\n\n\n')

            ec = o["ec"]
            if ec == 0:
                # OK !
                self._logger.info("got qq number: %s", o["uin"])
                # TODO save it to database
                self.goods += 1
                self.regdev.report_uin()
            elif ec == 2:
                # captcha error
                self._logger.info('capthcha error')
                if self.captcha_from == 'ruokuai':
                    # report error to ruokuai
                    paramDict = {
                            'username': self.rk_user, 
                            'password': self.rk_pass,
                            'softid': '57838',
                            'softkey': 'b61afeabc6d648c794354ceba073737c',
                            'id': self._rk_tid,
                            }
                    url = 'http://api.ruokuai.com/reporterror.json'
                    rk = ruokuai.APIClient()
                    con = rk.http_report_error(url, paramDict)
                    obj = json.loads(con)
                    self._logger.info('ruokuai returns: %s', con)
                    self._logger.info('ruokuai returns verify code: %s', obj['Result'])
                    self.verifycode = obj["Result"]

                self.input_captcha()
            elif ec == 4:
                # parameter error
                self._logger.info('paramter error, please check!')
                self.need_reg = False
            elif ec == 20:
                # need phone number to receive sms verify code
                self._logger.info('need send sms')
                self.input_phone()
                #if self.phone is None:
                #    self.need_reg = False
            elif ec == 21:
                # ERROR: blocked !!!
                self._logger.error('this ip is blocked! retry in 24 hours or change ip')
                self.need_reg = False
            elif ec == 26:
                # need send 1 to 10690700511 
                self._logger.info('need use a phone to send 1 to 10690700511')
                self.need_reg = False
            else:
                # unknown error code
                self._logger.info('unkown error code: %d', ec)


    def _format_query(self):
        qlist = ["verifycode={0}",
                "qzone_flag={1}",
                "country={2}",
                "province={3}",
                "city={4}",
                "isnongli={5}",
                "year={6}",
                "month={7}",
                "day={8}",
                "isrunyue={9}",
                "password={10}",
                "nick={11}",
                "email={12}",
                "other_email={13}",
                "elevel={14}",
                "sex={15}",
                "qzdate=",
                "jumpfrom={16}",
                "telphone={17}",
                "smsvc={18}",
                "csloginstatus={19}",
                "q5e1h3={20}", 
                ""]
        query = "&".join(qlist)
        return query.format(
                self.verifycode,    # verify code
                0,                  # qzone_flag
                self.country,       # country
                self.province,      # province
                self.city,          # city
                0,                  # isnongli
                self.year,          # year
                self.month,         # month
                self.day,           # day
                0,                  # isrunyue
                self.rsa_password,  # password
                self.nickname,      # nick
                "false",            # email
                "false",            # other_email
                self.elevel,        # elevel
                self.gender,        # sex
                58030,              # jumpfrom
                self.phone,         # phone
                self.smsvc,         # smsvc
                0,                  # csloginstatus
                "j9e0r0",           # q5e1h3
                )
        
    def __country_name(self):
        # print(list(self.location[self.country].keys()))
        return self.location[self.country]['n']
        
    def __province_name(self):
        return self.location[self.country][self.province]['n']
        
    def __city_name(self):
        return self.location[self.country][self.province][self.city]['n']
        
    def __str__(self):
        return '''QQReg(random={})
  nickname: {}
  password: {}
  gender: {}
  country: {}, {}
  province: {}, {}
  city: {}, {}
  birth: {}-{}-{}'''.format(self.if_rand, 
  self.nickname, 
  self.password, 
  self.gender, 
  self.country, self.__country_name(), 
  self.province, self.__province_name(), 
  self.city, self.__city_name(), 
  self.year, self.month, self.day)
  
    def __repr__(self):
        return self.__str__()

if __name__ == '__main__':
    qr = QQReg(random=True)
    
    print(qr)
   
    #qr.init_reg()
    #qr.input_captcha()
    qr.do_reg()
    
    
    
