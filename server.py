#!/usr/bin/env pyton3
#-*- encoding: utf-8 -*-

#import bottle
#from manager import ConfigManager

# class QQRegServer(object):
    
    # def __init__(self, *args, **kwargs):
        # config = kwargs.get('config')
        # if isinstance(config, ConfigManager):
            # # from config
            # pass
            
#from bottle import route, run
import time
import json
import base64
import hashlib
import zipfile
import bottle
import cork
import rsa
from datetime import datetime
from beaker.middleware import SessionMiddleware
import zclog

_logger = zclog.getLogger(__name__)
aaa = cork.Cork("admin_conf")
app = bottle.app()
session_opts = {
    'session.cookie_expires': True,
    'session.encrypt_key': 'please use a random key and keep it secret!',
    'session.httponly': True,
    'session.timeout': 3600 * 24,  # 1 day
    'session.type': 'cookie',
    'session.validate_key': True,
}
app = SessionMiddleware(app, session_opts)

_dbman = None

#check_login = None

@bottle.route('/hello')
def hello():
    return 'hello, world'


@bottle.route('/')
def index():
    bottle.redirect('/admin')
    
@bottle.get('/login') # or @route('/login')
def login():
    return '''
        <form action="/login" method="post">
            Username: <input name="username" type="text" />
            Password: <input name="password" type="password" />
            <input value="Login" type="submit" />
        </form>
    '''

@bottle.post('/login') # or @route('/login', method='POST')
def do_login():
    username = bottle.request.forms.get('username')
    password = bottle.request.forms.get('password')
    #if check_login is not None and check_login(username, password):
    #    return "<p>Your login information was correct.</p>"
    #else:
    #    return "<p>Login failed.</p>"
    #aaa.login(username, password)
    aaa.login(username, password, success_redirect='/admin', fail_redirect='/login')
    
@bottle.route('/logout')
def logout():
    aaa.logout(success_redirect='/login')
    
@bottle.route('/admin')
def admin():
    """Only admin users can see this"""
    aaa.require(role='admin', fail_redirect='/login')
    # roles = '; '.join('{}, {}'.format(*r) for r in aaa.list_roles()) 
    # users = '; '.join('{}, {}, {}, {}'.format(*u) for u in aaa.list_users())
    # cur_user = aaa.current_user
    # cur_user_str = '{}, {}'.format(cur_user.username, cur_user.role)
    # d = dict(
        # current_user=cur_user_str,
        # users=users,
        # roles=roles
    # )
    # print(d)
    # return d
    qzc_users = _dbman.query_users()
    qzc_devs = _dbman.query_devices()
    return bottle.template('tpl/admin.tpl', user='admin', users=qzc_users, devs=qzc_devs)

@bottle.route('/adduser', method="post")
def adduser():
    aaa.require(role='admin', fail_redirect='/login')
    uname = bottle.request.forms.get('uname')
    upass = bottle.request.forms.get('upass')
    ok = _dbman.add_user(uname, upass)
    if ok:
        bottle.redirect('/admin')
    else:
        return bottle.template('tpl/adduser_failed.tpl', name=uname, password=upass)


@bottle.route('/adddev', method="post")
def adddev():
    aaa.require(role='admin', fail_redirect='/login')
    dname = bottle.request.forms.get('dname')
    dpass = bottle.request.forms.get('dpass')
    ok = _dbman.add_dev(dname, dpass)
    if ok:
        bottle.redirect('/admin')
    else:
        return bottle.template('tpl/adddev_failed.tpl', name=dname)


@bottle.route('/admin/phones')
def admin_phones():
    aaa.require(role='admin', fail_redirect='/login')
    phones = _dbman.query_phones()
    return bottle.template('tpl/admin_phones.tpl', user='admin', phones=phones)


@bottle.route('/admin/sms')
def admin_sms():
    aaa.require(role='admin', fail_redirect='/login')
    sms = _dbman.query_sms()
    return bottle.template('tpl/admin_sms.tpl', user='admin', sms=sms)


@bottle.route('/admin/uin')
def admin_uin():
    aaa.require(role='admin', fail_redirect='/login')
    uin = _dbman.query_uin()
    return bottle.template('tpl/admin_uin.tpl', user='admin', uin=uin)

    
@bottle.route('/1/<name>/1', method='post')
def qqzc_init(name):
    """Initialize client, report phone numbers to server"""
    # 1. check username; 
    if not _dbman.user_exist(name):
        return 'not exist.'

    ip = bottle.request.environ.get('REMOTE_ADDR')
    _dbman.user_login(name, ip)

    # 2. phone number format: n
    #    >>> import base64
    #    >>> numbers = [number1, number2, ...]
    #    >>> bytes_str = b','.join(n.to_bytes(6, 'big') for n in numbers)
    #    >>> n = base64.b64encode(bytes_str)
    #    >>> n
    n = bottle.request.forms.get('n')
    if len(n) == 0:
        return 'phone number error'
    try:
        bytes_str = base64.b64decode(n)
    except Exception as e:
        return 'phone number error'
    else:
        numbers = [int.from_bytes(bi, 'big') for bi in bytes_str.split(b',')]
        _dbman.add_phones(name, numbers)
    return 'ok'

@bottle.route('/1/<name>/2')
def qqzc_smsvc(name):
    """send back sms verify code"""
    # 1. check username
    if not _dbman.user_exist(name):
        return 'not exist.'

    # 2. query which phone need to receive sms
    smsvc = _dbman.query_smsvc_usr(name, status=1)
    if smsvc is None or len(smsvc) == 0:
        return 'ok'

    #_logger.info('smsvc: %s', smsvc);
    L = []
    for sv in smsvc:
        if sv is None:
            continue
        _logger.info('need send smsvc phone: %s', sv.phone)
        b1 = int(sv.phone).to_bytes(6, 'big')
        b1 += b':'
        b1 += str(sv.id_).encode()
        L.append(b1)
    if len(L) > 0:
        bs = base64.b64encode(b','.join(L))
        _logger.info('return %s', bs)
        return bs
    return 'ok'

    # 2. sms verify code:
    #    >>> import base64
    #    >>> n = base64.b64encode(code.to_bytes(6, 'big')
    #    >>> n
    # the same applies to `c`.
    # n is the phone number and c is verify code
    n = bottle.request.forms.get('n')
    c = bottle.request.forms.get('c')
    i = bottle.request.forms.get('i')

    _logger.info('n=%s, c=%s, i=%s', n, c, i)

    try:
        id_ = int(i)
    except ValueError:
        _logger.warn('action id wrong: %s', i)
        return 'action id invalid'

    try:
        
        phone = base64.b64decode(n)
        smsvc = base64.b64decode(c)

        phone = str(int.from_bytes(phone, 'big'))
    except Exception as e:
        _logger.error(e)
        return 'verify code error'
    else:
        # TODO send to QQReg object
        # FIXME how do I know the action id?
        ok = _dbman.update_action(name, id_, phone, smsvc)

    if ok:
        return 'ok'
    else:
        return 'add failed'
    
@bottle.route('/1/<name>/3', method='post')
def qqzc_report(name):
    # client will post sms to this server
    #print(dir(bottle.request.files))
    #print(type(bottle.request.files))
    #print("bottle.request.files:")
    #for k,v in bottle.request.files.items():
    #    print('{}={}'.format(k,v))
    #print("bottle.request.forms:")
    #for k,v in bottle.request.forms.items():
    #    print('{}={}'.format(k,v))
    #print(type(bottle.request.body))
    #print(bottle.request.body)
    #raw = bottle.request.body.read()

    upload = bottle.request.files.get('filename')
    # name, ext = os.path.splitext(upload.filename)

    _logger.info('filename: %s', upload.filename)

    if upload.filename.endswith('.zip'):
        _logger.info('client send a zip file')
        tmpzip = 'tmp.zip'
        with open(tmpzip, 'wb') as f:
            raw = upload.file.read()
            f.write(raw)
        zf = zipfile.ZipFile(tmpzip)
        raw = zf.read(zf.namelist()[0])
    else:
        raw = upload.file.read()
    #_logger.info('recv file %d bytes:\n%s', len(raw), raw.decode('gbk'))
    #_logger.info('recv file %d bytes', len(raw))

    _dbman.add_smstext(name, raw.decode('gbk'))
    return 'ok'



def qqzc_report_old(name):
    """report total successful registrations TODAY"""
    # 1. check username
    if not _dbman.user_exist(name):
        return 'not exist.'
    
    # 2. TODO send back phones need to receive sms verify code

    # 3. TODO send back seccessful registrations TODAY
    return 'ok'


_dev_session = {}
_dev_challenge = {}


def check_devpass(devpass, cookie, cpass):
    m = hashlib.md5('{}-{}'.format(cookie, devpass).encode())
    h = base64.b64encode(m.digest()).decode()
    if h == cpass:
        return True
    return False

@bottle.route('/1/<dev>/4', method='get')
def qqzc_dev_login(dev):
    '''for devices to login to get a session id'''
    # 1. check dev name
    if not _dbman.dev_exist(dev):
        return 'not exist.'
    # check cookie
    cookie = bottle.request.get_cookie('n')
    cpass  = bottle.request.query.get('p')
    ip = bottle.request.environ.get('REMOTE_ADDR')
    if (cookie is None 
            or len(cookie) == 0 
            or ip not in _dev_challenge
            or cookie != _dev_challenge[ip]):
        # renew challenge
        s = '{0}-{1:.0f}'.format(ip, time.time())
        c = hashlib.md5(s.encode()).hexdigest()
        bottle.response.set_cookie('n', c)
        _dev_challenge[ip] = c
        return 'need authorization'

    d = _dbman.query_dev(dev)
    if d is None:
        return 'authorized failure'
    if not check_devpass(d.dpass, cookie, cpass):
        return 'authorized failure'
    else:
        # update device info
        _dbman.update_dev(dev, ip)
        # add a session
        c = '{}-{:.0f}-{}'.format(dev, time.time(), ip)
        s = hashlib.md5(c.encode()).hexdigest()
        _dev_session[ip] = s
        bottle.response.set_cookie('s', s)
        return 'ok'

def dev_check_session(dev, req):
    '''check if dev exists and if the session is valid'''
    # 1. check dev name
    if not _dbman.dev_exist(dev):
        _logger.info('device does not exist')
        return 1 # 'not exist.'
    # check session
    s = req.get_cookie('s')
    ip = req.environ.get('REMOTE_ADDR')
    _logger.info('ip: %s, session: %s', ip, s)
    if (s is None 
            or len(s) == 0
            or ip not in _dev_session
            or _dev_session[ip] != s):
        _logger.info('authorized failure')
        return 2 # 'authorized failure'

    return 0 # 'ok'


@bottle.route('/1/<dev>/5')
def qqzc_dev_getphones(dev):
    '''Machine will get a list of availabel phone numbers'''
    # 1. check session
    if 0 != dev_check_session(dev, bottle.request):
        return 'failed'

    # 2. return available phone numbers
    phones = _dbman.get_available_phones()
    if phones is None or len(phones) == 0:
        return '[]'

    phone_list = []
    for p in phones:
        phone_list.append({'number': p.phone, 'user': p.uname})

    # TODO return phones
    return json.dumps(phone_list)

@bottle.route('/1/<dev>/6')
def qqzc_dev_requestsmsvc(dev):
    '''dev wants a phone to recv smsvc'''
    # 1. check session
    if 0 != dev_check_session(dev, bottle.request):
        return 'failed'
    ns = bottle.request.query.get('n')
    nb = base64.b64decode(n.encode())
    nl = nb.split(b',')
    numbers = [str(int.from_bytes(n, 'big')) for n in nl]
    
    # 2. update phone status
    ids = _dbman.update_phone_status(numbers, 1, dev, ip)
    if ids is None:
        return 'fail'
    s = json.dumps(ids)
    _logger.info('sms request ids: %s', s)
    return s

@bottle.route('/1/<dev>/7')
def qqzc_dev_getsmsvc(dev):
    '''return the smsvc to dev'''
    # 1. check session
    if 0 != dev_check_session(dev, bottle.request):
        return 'failed'

    phone = bottle.request.query.get('p')
    when  = bottle.request.query.get('w')

    _logger.info('query phone %s after %s', phone, when)
    print('query phone {} after {}'.format(phone, when))

    when  = datetime.strptime(when, '%Y%m%d-%H%M%S')

    count = 0
    smstxt = ''

    while True:
        count += 1
        if count > 5:
            return 'timeout'
        smsvc = _dbman.query_smsvc(dev, phone, when)

        if smsvc is None:
            time.sleep(2)
            continue

        id_ = 0
        
        for s in smsvc:
            t = s.text
            #_logger.info('message: %s', t)
            if (t.find('[tencent]') > -1 
                    or t.find('【腾讯科技】') > -1
                    or t.find('[腾讯科技]') > -1):
                smstxt = t
                id_ = s.id_
                break

        if smstxt:
            break

    if len(smstxt) == 0:
        return 'timeout'

    _dbman.update_sms_status(id_, 1)

    #l = []

    #for v in smsvc:
    #    l.append({'phone':v.phone, 'code':v.code})

    #s = json.dumps(smsvc)
    codes = []
    for c in smstxt:
        a = ord(c)
        if a >= 0x30 and a <= 0x39:
            codes.append(c)
        else:
            break
    vc = ''.join(codes)
    _logger.info('smsvc response: %s', vc)
    return vc

@bottle.route('/1/<dev>/8', method='post')
def qqzc_dev_getuin(dev):
    '''Got a qq number. Recored it into database.'''
    uin         = bottle.request.forms.get('uin')
    ursapass    = bottle.request.forms.get('password')
    unick       = bottle.request.forms.get('nick')
    ucountry    = bottle.request.forms.get('country')
    uprovince   = bottle.request.forms.get('province')
    ucity       = bottle.request.forms.get('city')
    ubirth      = bottle.request.forms.get('birth')
    ugender     = bottle.request.forms.get('gender')
    uphone      = bottle.request.forms.get('phone')
    unongli     = bottle.request.forms.get('nongli')
    uregion     = bottle.request.forms.get('region')
    ip          = bottle.request.environ.get('REMOTE_ADDR')

    # password need decrypt
    with open('private.pem', 'rb') as f:
        priv = f.read()

    privkey = rsa.PrivateKey.load_pkcs1(priv)
    upass = rsa.decrypt(base64.b64decode(ursapass.encode()), privkey)

    # nongli and gender need convert to int
    try:
        nongli = int(unongli)
    except ValueError:
        if nongli.lower() == 'true':
            nongli = 1
        else:
            nongli = 0
    try:
        gender = int(ugender)
    except ValueError:
        if gender.lower() == 'female':
            gender = 2
        else:
            gender = 1

    ok = _dbman.add_uin(uin, upass, unick, 
            ucountry, uprovince, ucity, 
            ubirth, ugender, uphone, 
            unongli, uregion, ip, dev)
    _logger.info('add %s to database', uin)
    if ok:
        return 'ok'
    return 'fail'


@bottle.route('/1/<dev>/9')
def report_phone_status(dev):
    # 1. check session
    if 0 != dev_check_session(dev, bottle.request):
        return 'failed'

    phone  = bottle.request.query.get('p')
    status = bottle.request.query.get('t')
    try:
        t = int(status)
    except ValueError:
        return 'status is not correct'

    _dbman.update_phone_status2(phone, t)
    return 'ok'

    
def run_server(host, port, dbman):
    """start server"""
    #global check_login
    #check_login = check_login_func
    global _dbman
    _dbman = dbman
    bottle.run(app=app, host=host, port=port, debug=True)

if __name__ == '__main__':
    pass
    
