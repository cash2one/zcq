#!/usr/bin/env python3

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
import mmh3 # third-party module
import encryption
import ruokuai

GENDER_MALE = 1
GENDER_FEMALE = 2


class QQReg(object):
    """QQ registration class"""
    
    name_set = string.digits + string.ascii_letters
    
    init_url    = "http://zc.qq.com/cgi-bin/chs/numreg/init?r={}"
    getacc_url  = "http://zc.qq.com/cgi-bin/chs/numreg/get_acc_safe?r={}"
    sendsms_url = "http://zc.qq.com/cgi-bin/chs/common/sms_send_safe"
    monikey_url = "http://a.zc.qq.com/Cgi-bin/MoniKey?"
    captcha_url = "http://captcha.qq.com/getimage?aid=1007901&r={}"
    referer_url = "http://zc.qq.com/chs/index.html"
    #user_agent  = "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36"
    user_agent  = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:46.0) Gecko/20100101 Firefox/46.0"
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
        #self.phone_pool     = PhonePool(self.phone_list)
        self.captcha_path   = kwargs.get('captcha_path', 'captcha')
        self.logfile        = kwargs.get('log_file', 'QQReg.log')
        self.rk_user        = kwargs.get('rk_user', None)
        self.rk_pass        = kwargs.get('rk_pass', None)
        self.server         = kwargs.get('server', None)
        self.dev_name       = kwargs.get('dev_name', None)
        self.dev_session    = kwargs.get('dev_session', None)
        self.configfile     = kwargs.get('config', 'client.ini')

        # reg client
        #self.regdev = RegClient.from_session(self.dev_session, self.configfile)
        
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

        self.req_cache = 'request_cache'
        if not os.path.isdir(self.req_cache):
            try:
                os.makedirs(self.req_cache)
            except OSError as e:
                raise
                
        # for chs
        self.sig = None
        self.ticket = None
        
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
        #self.init_reg()
        self.init_cap_cookie()
        self.cap_union_check_new()
        self.cap_union_show_new()
        self.cap_union_getcapbysig_new()
        return True
        
        
    def input_captcha(self):
        ok = False
        while not ok:
            ok = self._input_captcha()
        self.__send_monikey("code", self.verifycode)
        self.safe_check()

    def _input_captcha(self):
        ok = self._refresh_captha()
        if not ok:
            return False
        if self.captcha_from == 'console':
            # read captcha from console
            self.answer = input("Please input what you see in \"{}\":".format(self.captcha_name))
            
            #ans = self.answer.split(';')
            try:
                ret = self.cap_union_verify_new(self.answer)
                ok,msg = ret
                if ok == 0:
                    return True
                else:
                    return False
            except TypeError:
                #print(ret)
                return False
            
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
                    'typeid': '6203',
                    'timeout': '100', # 90s? 
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
            # something like: {"Result":"45,103;90,99;217,79","Id":"9848b268-34d9-47d0-a324-fc0b45594e9c"}
            self.answer = obj["Result"]
            self._rk_tid = obj['Id']
            try:
                ret = self.cap_union_verify_new(self.answer)
                ok,msg = ret
                if ok == 0:
                    return True
                else:
                    paramKeys = ['username', 'password', 'softid', 'softkey', 'id']
                    paramDict = {
                            'username': self.rk_user, 
                            'password': self.rk_pass,
                            'softid': '57838',
                            'softkey': 'b61afeabc6d648c794354ceba073737c',
                            'id': self._rk_tid,
                            }
                    url = 'http://api.ruokuai.com/reporterror.json'
                    con = rk.http_report_error(url, paramDict, paramKeys)
                    obj = json.loads(con)
                    self._logger.info('report error to ruokuai')
                    self._logger.info('ruokuai returns: %s', con)
                    
            except TypeError:
                #print(ret)
                return False
            
        else:
            raise UnknownCaptchaFromException("Unknown captcha source")

        

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


            init_result_file = os.path.join(self.req_cache, "{}.res".format(self.start_time))
            with open(init_result_file, "ab+") as f:
                f.seek(0, 2)
                f.write(con)
                f.write(b'\n\n\n')

    def send_monikey_common(self):
        self.__send_monikey('nick', self.nickname)
        self.__send_monikey('password', self.password)
        self.__send_monikey('password_again', self.password)
        self.__send_monikey('year_value')
        self.__send_monikey('month_value')
        self.__send_monikey('day_value')
        self.__send_monikey('country_value')
        self.__send_monikey('province_value')
        self.__send_monikey('city_value')

    def __send_monikey(self, name, text=None):
    # TODO sleep for a while to send monikey request
        time.sleep(3)
        tm = '{0:.0f}'.format(time.time())
        tp = self.aq_input.get(name, 'year_value')
        if text is not None:
            query = '&'.join('{}|{}|{}'.format(ord(c), tp, tm) for c in text)
        else:
            query = '0|{}|{}'.format(tp, tm)
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
            
    
    def check_phone(self):
        # http://zc.qq.com/cgi-bin/common/check_phone?telphone=18049634161&r=0.31673819818619764&
        url = 'http://zc.qq.com/cgi-bin/common/check_phone?telphone={}&r={}'.format(self.phone, random.random())
        headers = {
                "User-Agent": self.user_agent,
                "Referer": self.referer_url
                }
        try:
            self._logger.info('requst %s', url)
            cookieprocessor = urllib.request.HTTPCookieProcessor(self.cookies)
            opener = urllib.request.build_opener(cookieprocessor)
            req = urllib.request.Request(url, None, headers)
            res = opener.open(req)
        except Exception as e:
            self._logger.critical(e)
            return False
        else:
            con = res.read()
            con = con.decode()
            self._logger.info('check_phone response: %s', con)
            o = json.loads(con)
            # something like
            # {"ec":0}
            ec = o['ec']
            return ec == 0
            
    

    def input_phone(self):
        if not self.phone:
            self.phone = self.next_phone()
        if not self.phone:
            self._logger.info('phone number exhausted')
            self.need_reg = False
            return
            
        ok = self.check_phone()
        if not ok:
            self._logger.error('Phone number invalid')
            return False
        self.__send_monikey('phone_num', self.phone)
            
        #self.elevel = 3
        do_next = True # if continue to register

        # send smsvc
        url = self.sendsms_url
        r = random.random()
        self._logger.info('use phone number %s to receive sms verify code.', self.phone)
        # telphone=18049634161&elevel=1&regType=1&nick=
        query = 'telphone={}&elevel=3&regType=1&nick={}&r={}'.format(self.phone, urllib.parse.quote(self.nickname), r)
        headers = {
                "User-Agent": self.user_agent,
                "Referer": self.referer_url
                }
        try:
            self.sms_from_dt = dt = time.strftime('%Y%m%d-%H%M00')
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
                if self.phone_from == 'console': 
                    self.smsvc = input('Please input sms verify code: ')
                elif self.phone == self.phone_from:
                    # receive phone from remote
                    # TODO use more elegant way
                    self._logger.info('use phone %s to receive sms', self.phone_from)
                    # TODO ask remote to receive sms verify code
                    if self.regdev is None:
                        self._logger.info('session %s is not binded to a client', self.dev_session)
                    else:
                        self.smsvc = self.regdev.get_smsvc(self.phone, dt)
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
                    if self.regdev is None:
                        self._logger.info('session %s is not binded to a client', self.dev_session)
                    else:
                        self.smsvc = self.regdev.get_smsvc(self.phone, dt)
            elif ec == 14:
                # already to limited number
                self._logger.info('this phone %s received up to limited sms.', self.phone)
                #if not self.phone:
                #    self.need_reg = False
                #else:
                #    self._logger.info('change to use phone %s', self.phone)
                self.regdev.report_phone_sms_limited(self.phone)
                self.phone = '' # self.next_phone()
                do_next = False
            elif ec == 16:
                # sms check error: no smsvc
                do_next = False

            elif ec == 4 or ec == 31:
                # phone format invalid
                self._logger.info('invalid phone: %s', self.phone)
                self.regdev.report_phone_invalid(self.phone)
                do_next = False
            else:
                self._looger.info('error code: %d, will retry later', ec)
                do_next = False

        return do_next

    
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
        return (maybephone.startswith('1') 
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
        # uoc
        uoc = '{0}-0-{1}-0-{1}-0-0-{2}'.format(
            len(self.nickname),
            len(self.password),
            len(self.nickname) + 2 * len(self.password),
            )
        cookie_uoc = self._new_cookie('uoc', uoc, '.zc.qq.com')
        self.cookies.set_cookie(cookie_uoc)

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
            self.need_reg = False
        else:
            self._logger.info("got getacc response")
            con = res.read()
            con1 = con.decode()
            self._logger.info(con1)
            o = json.loads(con1)
            filename = os.path.join(self.req_cache, self.start_time)

            with open(filename, "ab+") as f:
                f.write(b'getacc response: \n')
                f.write(con)
                f.write(b'\n\n\n')

            ec = o["ec"]
            if ec == 0:
                # OK !
                uin = o['uin']
                self._logger.info("got qq number: %s", o["uin"])
                # TODO save it to database
                self.goods += 1
                self.regdev.report_uin(uin, self.password,
                        nick=self.nickname,
                        phone=self.phone,
                        province=self.province,
                        country=self.country,
                        city=self.city,
                        birth='{}-{}-{}'.format(self.year, self.month, self.day),
                        gender=self.gender)
                # clean some parameter
                self.phone = '' 
                self.code  = ''
                self.smsvc = ''
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
                    self._logger.info('report error to ruokuai')
                    self._logger.info('ruokuai returns: %s', con)
                    #self._logger.info('ruokuai returns verify code: %s', obj['Result'])
                    #self.verifycode = obj["Result"]

                self.input_captcha()
            elif ec == 4:
                # parameter error
                self._logger.info('paramter error, please check!')
                self.need_reg = False
            elif ec == 16:
                # smsvc error
                self._logger.info('smsvc error, please check!')
                dt = self.sms_from_dt
                #self.smsvc = 
                if self.phone_from == 'console': 
                    self.smsvc = input('Please input sms verify code: ')
                elif self.phone == self.phone_from:
                    # receive phone from remote
                    # TODO use more elegant way
                    self._logger.info('use phone %s to receive sms', self.phone_from)
                    # TODO ask remote to receive sms verify code
                    if self.regdev is None:
                        self._logger.info('session %s is not binded to a client', self.dev_session)
                    else:
                        self.smsvc = self.regdev.get_smsvc(self.phone, dt)
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
                    if self.regdev is None:
                        self._logger.info('session %s is not binded to a client', self.dev_session)
                    else:
                        self.smsvc = self.regdev.get_smsvc(self.phone, dt)
            elif ec == 20:
                # need phone number to receive sms verify code
                self._logger.info('need send sms')
                self.need_reg = self.input_phone()
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
                "q6p3={20}",
                "tk={21}",
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
                "p3r7",             # q6p3
                self.ticket,        # tk
                )
        
    def __country_name(self):
        # print(list(self.location[self.country].keys()))
        return self.location[self.country]['n']
        
    def __province_name(self):
        return self.location[self.country][self.province]['n']
        
    def __city_name(self):
        return self.location[self.country][self.province][self.city]['n']
        
    def __repr__(self):
        return '''QQReg(random={})\n  nickname: {}\n  password: {}\n  gender: {}\n  country: {}, {}\n  province: {}, {}\n  city: {}, {}\n  birth: {}-{}-{}'''.format(
                self.if_rand, 
                self.nickname, 
                self.password, 
                self.gender, 
                self.country, self.__country_name(), 
                self.province, self.__province_name(), 
                self.city, self.__city_name(), 
                self.year, self.month, self.day)
    
    
    @staticmethod
    def _new_cookie(name, value, domain='qq.com', path='/', expires=None):
        if expires is not None:
            tm = time.strptime(expires, '%a, %d %b %Y %H:%M:%S GMT')
            expires = round(time.mktime(tm))
        return http.cookiejar.Cookie(
            '0',        # version
            name,       # name
            value,      # value
            None,       # port
            False,      # port_specified
            domain,     # domain
            True,       # domain_specified
            False,      # domain_initial_dot
            path,       # path,
            True,       # path_specified
            False,      # secure
            expires,    # expires
            True,       # discard
            None,       # comment
            None,       # comment_url
            ()          # rest
            )
        
        
    def init_cap_cookie(self):
        # cookie:
        # pgv_pvid=7468445178; pgv_info=ssid=s6826362800; pgv_pvi=9291276288; pgv_si=s4117469184; TDC_token=3794683095
        # a = Math.round(Math.random() * 2147483647) * (new Date).getUTCMilliseconds() % 1E10
        # pgv_pvid = $a; path=/; domain=qq.com; expires=Sun, 18 Jan 2038 00:00:00 GMT;"
        # c = Math.round(Math.random() * 2147483647) * (new Date).getUTCMilliseconds() % 1E10
        # pgv_info=ssid=s + $c + ; path=/; domain=qq.com;
        def _cv():
            return str(round(random.random()*2147483647 * (time.time()*1000) % 1e10))
        
        pgv_pvid = _cv()
        cookie_pgv_pvid = self._new_cookie('pgv_pvid', pgv_pvid, expires='Sun, 18 Jan 2038 00:00:00 GMT')
        
        pgv_info = 's'+_cv()
        cookie_pgv_info = self._new_cookie('pgv_info', pgv_info)
        
        pgv_si = 's'+_cv()
        cookie_pgv_si = self._new_cookie('pgv_si', pgv_si)
        
        pgv_pvi = _cv()
        cookie_pgv_pvi = self._new_cookie('pgv_pvi', pgv_pvi, expires="Sun, 18 Jan 2038 00:00:00 GMT")
        
        # TDC_token=3794683095
        TDC_token = str(abs(mmh3.hash('foo', 32)))
        cookie_TDC_token = self._new_cookie('TDC_token', TDC_token,)
        
        # used only for captcha
        self.cap_cookie = http.cookiejar.CookieJar()
        self.cap_cookie.set_cookie(cookie_pgv_pvid)
        self.cap_cookie.set_cookie(cookie_pgv_info)
        self.cap_cookie.set_cookie(cookie_pgv_si)
        self.cap_cookie.set_cookie(cookie_pgv_pvi)
        self.cap_cookie.set_cookie(cookie_TDC_token)
        
        # save them to cookies
        self.cookies.set_cookie(cookie_pgv_pvid)
        self.cookies.set_cookie(cookie_pgv_info)
        self.cookies.set_cookie(cookie_pgv_si)
        self.cookies.set_cookie(cookie_pgv_pvi)
        self.cookies.set_cookie(cookie_TDC_token)
        
        cookieprocessor = urllib.request.HTTPCookieProcessor(self.cap_cookie)
        self.cap_opener = urllib.request.build_opener(cookieprocessor)
        

    def cap_union_check_new(self):
        # ?aid=1600000592&clientype=2&lang=1028
        # https://ssl.captcha.qq.com/cap_union_check_new?aid=1600000592&captype=&protocol=https&uin=&clientype=2&rand=0.9338748481637782
        url = 'https://ssl.captcha.qq.com/cap_union_check_new?aid=1600000592&clientype=2&captype=&protocol=https&uin=&rand={}'.format(random.random())
        #url += '&collect=BlSUMIWZKFe2aT-aI6kx_9LIPs5DiH8V90kMGRwVpD_b_VYcpoE78xdI4p-M90sNLPeMPO51XDt51LL-mqHv1ZIrxUnoX3QDNcS9sXlU1ut3k_6aTxJp4P4FaS4nBZARiWGBR00bY0Xnj2OHwC_ZDOWNzQSENGdElQP9fBgs4mE2-ntYyc4Zh5E6K_JkjaGtk2hzz-t3w2DUouk74NwNLUBts3Qh0AFxa4qZ8fO0-ZImf-WDI59sxUW5UHHXGuMAEOtw0J28qmefZyueVpm1PHXP9M6n524sOwP6tVbvd8w4U7nzCZEcrca1LJvs7gwy_hqyOm4q-nmYneodPySjYhlshJjq5IA1UNdOWCULU1mN9NTUecnDE3ETSSYdpaESeX10jCVeRnXwxkMjHokECjjj5XZt-69rTVcXQ_OHVIZ2OjdhVVVp0vlCGvOPRnvpJYnXrKc-RMHH89mOTCaizp_i_3qhK96Z0IZyAwoLLFInx2AhVONLAf7LeJRhiryvhqg34qUDuSwHS1SQWw5VVQ**'
        headers = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36', 
                #self.user_agent,
                "DNT": "1",
                "Referer": 'https://ssl.captcha.qq.com/template/placeholder.html?aid=1600000592&captype=&protocol=https&uin=&clientype=2'
                }
        try:
            st = self.start_time
        except AttributeError:
            st = self.start_time = time.strftime("%Y%m%d-%H%M%S")
            
        try:
            req = urllib.request.Request(url, None, headers)
            #res = opener.open(req)
            #res = urllib.request.urlopen(url)
            res = self.cap_opener.open(url)
            self._logger.info('request for cap_union_check_new: %s', url)
            for ck in self.cap_cookie:
                self._logger.info('Cookie: {}={}; path={}; domain={}'.format(ck.name, ck.value, ck.path, ck.domain))
        except Exception as err:
            self._logger.error(err)
        else:
            con = res.read()
            fn = os.path.join(self.req_cache, 'cap_union_check_new_'+self.start_time)
            with open(fn, 'wb') as f:
                f.write(con)
            con = con.decode()
            self._logger.info('cap_union_check_new: %s', con)
            obj = json.loads(con)
            # response like:
            #  {"state":"1","ticket":"","captype":"1","subcaptype":"7"}
            #
            print(con)
            
            
    def cap_union_show_new(self):
        url = 'https://ssl.captcha.qq.com/cap_union_show_new?aid=1600000592&captype=&protocol=https&uin=&clientype=2&rand={}&width=284'.format(random.random())
        headers = {
                "User-Agent": self.user_agent,
                "Referer": self.referer_url
                }
        try:
            req = urllib.request.Request(url, None, headers)
            #res = opener.open(req)
            #res = urllib.request.urlopen(url)
            res = self.cap_opener.open(url)
        except Exception as err:
            self._logger.error(err)
        else:
            con = res.read()
            #con = con.decode()
            #obj = json.loads(con)
            fn = os.path.join(self.req_cache, 'cap_union_show_new_'+self.start_time)
            with open(fn, 'wb') as f:
                f.write(con)
            con = con.decode()
            _start = con.find('var n=')
            if _start < 0:
                self._logger.warn('cap_union_show_new: cap sig not found, please check cap_union_show_new_%s', self.start_time)
                return
            _start += 6 # skip `var n=`
            quote = con[_start]
            _start += 1 # skip quote
            _end = con.find(quote, _start)
            if _end < 0:
                self._logger.warn('cap_union_show_new: cap sig not found, please check cap_union_show_new_%s', self.start_time)
                return 
            self.sig = con[_start:_end]
            self._logger.info('cap_union_show_new: cap sig: %s', self.sig)
            return self.sig
            
    def cap_union_getcapbysig_new(self):
        # https://ssl.captcha.qq.com/cap_union_getcapbysig_new?aid=1600000592&captype=&protocol=https&uin=&clientype=2&rand=0.08952814612229298&width=284&rand=0.1922499975483858&sig=c012Qj3yBS76v-p46iKPlyXOtmirbFtlUXhoHBmd2hH_Utoo0WhT8HVIj19lL8EnylzYoMzO8N5JVqZxYJRbija9hraEfcTNgup_Ghdmwb4RBuUjAmaNDNqwdvhx9tpuwddJ_5krh9Q7tgB3Zsz8zcbwCDJqYVAAjhZJFbFBcwhP4o*
        url = 'https://ssl.captcha.qq.com/cap_union_getcapbysig_new?aid=1600000592&captype=&protocol=https&uin=&clientype=2&rand={}&width=284&sig={}'.format(random.random(), self.sig)
        headers = {
                "User-Agent": self.user_agent,
                "Referer": self.referer_url
                }
        try:
            req = urllib.request.Request(url, None, headers)
            #res = opener.open(req)
            #res = urllib.request.urlopen(url)
            res = self.cap_opener.open(url)
        except Exception as err:
            self._logger.error(err)
        else:
            con = res.read()
            #con = con.decode()
            #obj = json.loads(con)
            fn = os.path.join(self.req_cache, 'cap_union_getcapbysig_new_{}.jpg'.format(self.start_time))
            self.captcha_name = fn
            with open(fn, 'wb') as f:
                f.write(con)
            self._logger.info('cap_union_getcapbysig_new: save image to %s', fn)
        
    
    def cap_union_verify_new(self, ans):
        # https://ssl.captcha.qq.com/cap_union_verify_new?aid=1600000592&captype=&protocol=https&uin=&clientype=2&rand=0.9338748481637782&width=284&rand=0.028523676957008748&capclass=7&sig=c01vKYGoiyikVwC59OpDZGkbrPZ5uXlc75gFRMybYfCEdGOVckVrv_WJnfwGMVjeN67zPlP6qsibS0c4yY0kruqsuq31nU8-7bkf7A0dx5h9GSJTdXJzaDHAuu0vIWCKXAlOeEXyN5tUjKYYhMsGNdt7WONPxpXyDb4lq9MqeTmqxE*&ans=265,75;115,90;64,50;92,149;
        if isinstance(ans, str):
            _ans = ans
        elif isinstance(ans, (list, tuple)):
            _ans = ';'.join(ans)
        else:
            raise ValueError('cap_union_verify_new() method expects a str, list or tuple parameter')
        url = 'https://ssl.captcha.qq.com/cap_union_verify_new?aid=1600000592&captype=&protocol=https&uin=&clientype=2&rand=0.9338748481637782&width=284&rand={}&capclass=7&sig={}&ans={}'.format(random.random(), self.sig, _ans)
        headers = {
                "User-Agent": self.user_agent,
                "Referer": self.referer_url
                }
        try:
            req = urllib.request.Request(url, None, headers)
            #res = opener.open(req)
            #res = urllib.request.urlopen(url)
            res = self.cap_opener.open(url)
        except Exception as err:
            self._logger.error(err)
        else:
            con = res.read()
            # response are like:
            # {"errorCode":"6" , "randstr" : "" , "ticket" : "" , "errMessage":"éªŒè¯å¤±è´¥ï¼Œè¯·é‡è¯•ã€‚"}
            # {"errorCode":"0" , "randstr" : "@rtl" , "ticket" : "t02DJMvj6cV5FyMfYj2c6awCYPPoaVrAJlUWyu7LO-ISZUeEmCsSkl4jAogHFEesweNwJpNjFA39fGgDTuMqrWPVbfgJLu9N-p4" , "errMessage":"éªŒè¯å¤±è´¥ï¼Œè¯·é‡è¯•ã€‚"}
            fn = os.path.join(self.req_cache, 'cap_union_verify_new_'+self.start_time)
            with open(fn, 'wb') as f:
                f.write(con)
            con = con.decode()
            self._logger.info('cap_union_verify_new: %s', con)
            obj = json.loads(con)
            ec = int(obj['errorCode'])
            msg = obj['errMessage']
            if ec == 0:
                self.verifycode = obj['randstr']
                self.ticket = obj['ticket']
                #return True
            elif ec == 50:
                # verify error
                pass
            elif ec == 6:
                pass
            return ec,msg
            
            
    def safe_check(self):
        # http://zc.qq.com/cgi-bin/chs/common/safe_check?r=0.1304640745673129
        url = 'http://zc.qq.com/cgi-bin/chs/common/safe_check?r={}'.format(random.random())
        
        query = self._format_query()
        
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
            #self.need_reg = False
        else:
            self._logger.info("safe_check response")
            con = res.read()
            con1 = con.decode()
            self._logger.info(con1)
            o = json.loads(con1)
            filename = os.path.join(self.req_cache, self.start_time)

            with open(filename, "ab+") as f:
                f.write(b'safe_check response: \n')
                f.write(con)
                f.write(b'\n\n\n')
            
            # con: something like
            # {"VerifyCodeResult":"2","ec":0,"elevel":"3","safeverifyResult":"3"}
            ec = o["ec"]
            self.elevel = elevel = int(o["elevel"])
            if ec == 0:
                if elevel == 3:
                    # need to receive sms verify code
                    self.need_reg = self.input_phone()
                elif elevel == 4:
                    # need to send sms verify codecs
                    self.need_reg = False
                elif elevel == 6:
                    # url = "error.html?ec={}".format(ec)
                    raise Exception("unknown safe_check elevel 6")
                else:
                    # phone is not neccessary
                    pass
            else:
                raise Exception('Unknown safe_check error code')
            
    def _print_ticket(self):
        print('sig:', self.sig)
        print('ticket:', self.ticket)
        
    def _test_cap_union(self):
        self.init_reg()
        self.cap_union_check_new()
        self.cap_union_show_new()
        self.cap_union_getcapbysig_new()
        s = input('Please input coordinates({}):'.format(self.captcha_name))
        ans = s.split(';')
        try:
            ret = self.cap_union_verify_new(ans)
            ok,msg = ret
            if ok == 0:
                self._print_ticket()
            # elif ok == 6:
                # print('验证坐标错误')
            # elif ok == 50:
                # print('验证坐标错误')
            else:
                #print('Unknown errorcode:', ok)
                #print('Please check cap_union_verify_new_'+self.start_time)
                print('error:', ok)
                print('message:', msg)
        except TypeError:
            print(ret)


    def _test_report_uin(self, uin):
        self.regdev.report_uin(uin, self.password,
                nick=self.nickname,
                phone=self.phone,
                province=self.province,
                country=self.country,
                city=self.city,
                birth='{}-{}-{}'.format(self.year, self.month, self.day),
                gender=self.gender)



if __name__ == '__main__':
    qr = QQReg(random=True, captcha='ruokuai', rk_user='zbqf109', rk_pass='a353535')
    
    #print(qr)
   
    #qr.init_reg()
    #qr.input_captcha()
    qr.do_reg()
    #qr._test_cap_union()
    #qr.init_cap_cookie()
    #qr.cap_union_check_new()
    
    
    
