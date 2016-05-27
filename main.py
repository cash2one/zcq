#!/usr/bin/env python3
#-*- encoding: utf-8 -*-

import pyzcqq
import manager
import server
import database

class UnknownPhoneFromError(Exception): pass

# qmb = None

class QManagerBackend(object):
    def __init__(self, config):
        self.cm = cm = manager.ConfigManager(config)
        db_type = 'mysql' # TODO make this flexible
        db_host = cm.db_host 
        db_port = cm.db_port
        db_user = cm.db_user
        db_pass = cm.db_pass
        db_name = cm.db_name
        self.dbman = database.QzcDatabaseManager(db_type, 
                db_host, db_port, db_user, db_pass, db_name)
        
    def start(self):
        cm = self.cm
        #if cm.phone_from == 'console':
        #    # from console
        #    qr = pyzcqq.QQReg(random=int(cm.random), phone='console')
        #    qr.do_reg()
        #elif cm.phone_from == 'remote':
            # from remote, will start http server
        server.run_server(cm.server_host, int(cm.server_port), self.dbman)
        #else:
        #    raise UnknownPhoneFromError('unknown phone from: {}'.format(cm.phone_from))
            
    # def check_login(self, name, password):
        # cm = self.cm
        # if name == cm.admin_name and password == cm.admin_pass:
            # return True
        # return False

# def check_login(name, password):
    # global qmb
    # if qmb is None:
        # return False
    # return qmb.check_login(name, password)
    
if __name__ == '__main__':
    qmb = QManagerBackend('server.ini')
    qmb.start()

    
    
