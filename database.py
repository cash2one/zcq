#!/usr/bin/env python3
#-*- encoding: utf-8 -*-

"""Database connection.
"""

import zclog
from datetime import datetime
import sqlalchemy
import sqlalchemy.ext.declarative 
from sqlalchemy import Column, ForeignKey, MetaData, Table
from sqlalchemy.types import VARCHAR, Integer, DATETIME
from sqlalchemy.orm import mapper, sessionmaker

_logger = zclog.getLogger(__name__)

BaseModel = sqlalchemy.ext.declarative.declarative_base()

class QzcUser(object):
    def __init__(self):
        self.name = ''
        self.password = ''
        self.total = ''
        
class QzcUsers(BaseModel):
    __tablename__ = 'users'
    name = Column('name', VARCHAR(20), primary_key=True)
    password = Column('password', VARCHAR(64))
    total = Column('total', Integer)

    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.total = 0

    def __repr__(self):
        return 'User(name={}, password={}, total={})'.format(self.name, self.password, self.total)

    #def __str__(self):
    #    return self.__repr__()
    
class QZcUserLogins(BaseModel):
    __tablename__ = 'logins'
    id_ = Column('id', Integer, primary_key=True)
    logdate = Column('logdate', DATETIME)
    ip = Column('ip', VARCHAR(20))
    uname = Column('uname', VARCHAR(20), ForeignKey('users.name'))
    
class QzcUserPhones(BaseModel):
    __tablename__ = 'userphones'
    id_ = Column('id', Integer, primary_key=True)
    phone = Column('phone', VARCHAR(20))
    adate = Column('adate', DATETIME)
    uname = Column('uname', VARCHAR(20), ForeignKey('users.name'))
    udate = Column('udate', DATETIME)
    total = Column('total', Integer)
    status = Column('status', Integer)

    def __init__(self, name, phone):
        self.phone = phone
        self.adate = datetime.now()
        self.uname = name
        self.udate = self.adate
        self.total = 0
        self.status = 0

    def __repr__(self):
        return 'Phone(number={}, uname={}, adate={}, udate={})'.format(self.phone, self.uname, self.adate, self.udate)
    
class QzcActions(BaseModel):
    __tablename__ = 'actions'
    id_ = Column('id', Integer, primary_key=True)
    ip = Column('ip', VARCHAR(20))
    uname = Column('uname', VARCHAR(20), ForeignKey('users.name'))
    uphone = Column('uphone', VARCHAR(20))
    uin = Column('uin', VARCHAR(30))
    adate = Column('adate', DATETIME)
    code = Column('code', VARCHAR(10))
    smsvc = Column('smsvc', VARCHAR(10))
    region = Column('region', VARCHAR(20))
    trytimes = Column('trytimes', Integer)

class QzcDevs(BaseModel):
    __tablename__ = 'devices'
    id_ = Column('id', Integer, primary_key=True)
    ip  = Column('ip', VARCHAR(20))
    dname = Column('dname', VARCHAR(20))
    dpass = Column('password', VARCHAR(64))
    duuid = Column('duuid', VARCHAR(128))
    status = Column('status', Integer)
    
    def __init__(self, name):
        self.dname = name
        self.ip = ""
        self.duuid = ""
        self.status = 0

    def __repr__(self):
        return 'Device(name={}, uuid={})'.format(self.dname, self.duuid)

class QzcSmsvc(BaseModel):
    __tablename__ = 'smsvc'
    id_             = Column('id',           Integer, primary_key=True)
    phone           = Column('phone',        VARCHAR(20))
    devip           = Column('devip',        VARCHAR(20))
    code            = Column('code',         VARCHAR(20))
    devname         = Column('devname',      VARCHAR(20))
    devsession      = Column('devsession',   VARCHAR(128))
    request_time    = Column('request_time', DATETIME)
    clientip        = Column('clientip',     VARCHAR(20))
    response_time   = Column('response_time',DATETIME)
    status          = Column('status',       Integer)

    def __init__(self, phone, devname, devip, devsession=''):
        self.phone = phone
        self.devip = devip
        self.devname = devname
        self.devsession = devssion
        self.request_time = datetime.now()
        self.clientip = ''
        self.response_time = ''
        self.status = 0

class QzcUin(BaseModel):
    __tablename__ = 'uin'
    uin         = Column('uin', VARCHAR(100), primary_key=True)
    password    = Column('password', VARCHAR(100)) 
    nick        = Column('nick', VARCHAR(100)) 
    country     = Column('country', VARCHAR(100)) 
    province    = Column('province', VARCHAR(100)) 
    city        = Column('city', VARCHAR(100)) 
    region      = Column('region', VARCHAR(20)) 
    birth       = Column('birth', VARCHAR(20)) 
    nongli      = Column('nongli', Integer) 
    gender      = Column('gender', Integer) 
    phone       = Column('phone', VARCHAR(20)) 
    ip          = Column('ip', VARCHAR(20)) 
    dev         = Column('dev', VARCHAR(20))
    adate       = Column('adate', DATETIME) 
    status      = Column('status', Integer) 

    def __init__(self, uin, upass, unick='', 
            ucountry='', uprovince='', ucity='', 
            ubirth='', ugender=1, uphone='', 
            nongli=0, uregion='', uip='', devname=''):
        self.uin        = uin
        self.password   = upass
        self.nick       = unick
        self.country    = ucountry
        self.province   = uprovince
        self.city       = ucity
        self.birth      = ubirth
        self.nongli     = nongli
        self.gender     = ugender
        self.phone      = uphone
        self.region     = uregion
        self.ip         = uip
        self.dev        = devname
        self.adate      = datetime.now()
        self.status     = 0

    def __repr__(self):
        return 'QQ({}, nick={})'.format(self.uin, self.nick)

class QzcDatabaseManager(object):
    
    def __init__(self, db_type, db_host, db_port, db_user, db_pass, db_name):
        self.db_type = db_type
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name
        
        uri = "{}://{}:{}@{}:{}/{}".format(db_type, db_user, db_pass, db_host, db_port, db_name)
        print(uri)
        
        self.engine       = sqlalchemy.create_engine(uri)
        #self.connection  = self.engine.connect()
        self.metadata     =  MetaData(self.engine)
        self.users_table  = Table('users',      self.metadata, autoload=True)
        self.login_table  = Table('logins',     self.metadata, autoload=True)
        self.phone_table  = Table('userphones', self.metadata, autoload=True)
        self.action_table = Table('actions',    self.metadata, autoload=True)
        self.device_table = Table('devices',    self.metadata, autoload=True)
        self.smsvc_table  = Table('smsvc',      self.metadata, autoload=True)
        self.uin_table    = Table('uin',        self.metadata, autoload=True)        

        #mapper(QzcUsers,        self.users_table)
        #mapper(QZcUserLogins,   self.login_table)
        #mapper(QzcUserPhones,   self.phone_table)
        #mapper(QzcActions,      self.action_table)
        #mapper(QzcDevs,         self.device_table)
        #mapper(QzcSmsvc,        self.smsvc_table)
        #mapper(QzcUin,          self.uin_table)
        
        self.session = sessionmaker(bind=self.engine)()
    
    def query(self, table, *args, **kwargs):
        # query some table
        if table == 'users':
            return self.query_users(table, args, kwargs)
        elif table == 'logins':
            return self.query_logins(table, args, kwargs)
        # if table == 'users':
            # return self.query_users(table, args, kwargs)
        # if table == 'users':
            # return self.query_users(table, args, kwargs)
        elif table == 'devices':
            return self.query_devices(table, args, kwargs)
            
    def query_users(self, *args, **kwargs):
        # query users
        query = self.session.query(QzcUsers)
        #u = query.first()
        #print(type(u))
        ##print(dir(u))
        #print('name=\"{}\", password=\"{}\", total=\"{}\"'.format(u.name, u.password, u.total))
        us = query.all()
        #print(type(us))
        #for u in us:
        #    print('name=\"{}\", password=\"{}\", total=\"{}\"'.format(u.name, u.password, u.total))
        return us

    def add_user(self, uname, upass):
        # add a new user
        try:
            u = QzcUsers(uname, upass)
            self.session.add(u)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            _logger.error(e)
            return False
        else:
            return True

    def user_exist(self, name):
        # check if a user exists
        query = self.session.query(QzcUsers)
        u = query.filter_by(name=name).first()
        # print(u)
        if u is None:
            return False
        return True

    def add_phones(self, name, phones):
        # add phones
        query = self.session.query(QzcUserPhones)
        for n in phones:
            _p = query.filter_by(phone=n).first()
            if _p:
                # already exists
                _p.udate = datetime.now()
            else:
                # add to database
                phone = QzcUserPhones(name, n)
                self.session.add(phone)
        try:
            self.session.commit()
        except Exception as e:
            _logger.error(e)
            self.session.rollback()
            return False
        else:
            return True

    def query_phones(self):
        # query all user phones
        query = self.session.query(QzcUserPhones)

        ps = query.all()
        return ps

    def update_action(self, uname, act_id, phone, smsvc):
        #query = self.session.query(QzcActions)
        #act = query.filter_by(phone=phone, uname=uname).first()

        #if act is None:
        #    _logger.warn('Action(phone=%s, name=%s) not in this database', phone, uname)
        #    return False

        #return True
        query = self.session.query(QzcSmsvc)
        record = query.filter_by(id_=act_id).first()

        _logger.info('phone=%s, smsvc=%s, id_=%d, status=%d', phone, smsvc, act_id, record.status)

        record.code = smsvc
        record.status = 1 # update status
        try:
            self.session.commit()
        except Exception as e:
            _logger.error(e)
            self.session.rollback()
            return False
        else:
            return True

    def query_devices(self, *args, **kwargs):
        # query devices
        query = self.session.query(QzcDevs)
        ds = query.all()
        return ds

    def add_dev(self, dname):
        # add a new device 
        try:
            u = QzcDevs(dname)
            self.session.add(u)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            _logger.error(e)
            return False
        else:
            return True

    def update_phone_status(self, phones, status, devname='', devip='', devsession=''):
        # 1. update phone status
        query = self.session.query(QzcUserPhones)
        for p in phones:
            dbphone_item = query.filter_by(phone=p).first()
            if dbphone_item is None:
                continue
            dbphone_item.status = status
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            _logger.error(e)
            return 
        else:
            # return True
            pass

        # 2. update smsvc
        smsreq_list = []
        for p in phones:
            smsreq = QzcSmsvc(p, devname, devip, devsession)
            smsreq_list.append(smsreq)
        try:
            self.session.add_all(smsreq_list)
            self.session.commit()
        except Exception as e:
            _logger.error(e)
            self.session.rollback()
            return 
        else:
            pass

        return [smsreq.id_ for smsreq in smsreq_list]

    def query_smsvc_dev(self, devname):
        # query smsvc table where devname=devname and status=1
        # status code:
        #   0: waiting to get smsvc code
        #   1: smsvc got, wating to send to dev
        #   2: smsvc already is sent to dev
        query = self.session.query(QzcSmsvc)
        vc = query.filter_by(devname=devname, status=1)
        if vc is None:
            return 
        for v in vc:
            v.status = 2 # already sent
        try:
            self.session.commit()
        except Exception as e:
            _logger.error(e)
            self.session.rollback()
            return 
        else:
            return vc

    def add_uin(self, uin, upass, unick, 
            ucountry, uprovince, ucity, 
            ubirth, ugender, uphone, unongli, uregion, 
            ip, dev):
        uin = QzcUin(uin, upass, unick, 
                ucountry, uprovince, ucity, 
                ubirth, ugender, uphone, unongli, uregion, 
                ip, dev)

        try:
            self.session.add(uin)
            self.commit()
        except Exception as e:
            _logger.error(e)
            self.session.rollback()
            return False
        else:
            return True

    def query_smsvc_usr(self, name, status):
        # 1. query phone numbers
        _logger.info('query name %s', name)
        query1 = self.session.query(QzcUserPhones)
        phones = query1.filter_by(uname=name).all()

        _logger.info('user %s phones: %s', name, phones)

        # 2. query smsvc
        query2 = self.session.query(QzcSmsvc)
        # in very rare cases, one phone may receive more than one smsvc
        # and how should we handle that?
        smsvc = [query2.filter_by(phone=p.phone, status=status).first() for p in phones]
        _logger.info('smsvc list: %s', smsvc)
        return smsvc
    
    def close(self):
        self.session.close()

    def __del__(self):
        self.close()
        

if __name__ == '__main__':
    dbman = QzcDatabaseManager('mysql', 'localhost', '306', 'qqzc', '123456', 'qqzc')
    q = dbman.query_users()
    print(q)
    #print(type(q))
    #print(dir(q))
    #dbman.add_user('2', '')
    #q = dbman.query_users()
    #print(q)
    #if dbman.user_exist('2'):
    #    print('user 2 exists')
    #else:
    #    print('user 2 not exists')
    #if dbman.user_exist('a'):
    #    print('user a exists')
    #else:
    #    print('user a not exists')
    #dbman.add_phones('1', ['18049634161'])
    dbman.close()
    
    
    
