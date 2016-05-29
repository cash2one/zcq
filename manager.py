#!/usr/bin/env python3
#-*- encoding: utf-8 -*-

import configparser

class ConfigManager(object):
    
    def __init__(self, configfile):
        self.config = configparser.ConfigParser()
        self.config.read(configfile)
        
    @property
    def db_user(self):
        return self.config['database']['db_user']

    @property
    def db_pass(self):
        return self.config['database']['db_pass']
    
    @property
    def db_host(self):
        return self.config['database']['db_host']
    
    @property
    def db_port(self):
        return self.config['database']['db_port']

    @property
    def db_name(self):
        return self.config['database']['db_name']

    @property
    def server_host(self):
        return self.config['server']['svr_host']
    
    @property
    def server_port(self):
        return self.config['server']['svr_port']
    
    @property
    def admin_name(self):
        return self.config['admin']['admin_name']
    
    @property
    def admin_pass(self):
        return self.config['admin']['admin_pass']
    

if __name__ == '__main__':
    pass
    
