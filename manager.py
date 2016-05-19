#!/usr/bin/env python3
#-*- encoding: utf-8 -*-

import configparser

class ConfigManager(object):
    
    def __init__(self, configfile):
        self.config = configparser.ConfigParser()
        self.config.read(configfile)
        
    @property
    def random(self):
        return self.config['Registration']['random']
        
    @property
    def region(self):
        return self.config['Registration']['region']
    
    @property
    def phone_from(self):
        return self.config['Registration']['phone_from']
    
    @property
    def nick(self):
        return self.config['Registration']['nick']
    
    @property
    def password(self):
        return self.config['Registration']['password']
    
    @property
    def gender(self):
        return self.config['Registration']['gender']
    
    @property
    def country(self):
        return self.config['Registration']['country']
    
    @property
    def province(self):
        return self.config['Registration']['province']
    
    @property
    def city(self):
        return self.config['Registration']['city']
    
    @property
    def birth_year(self):
        return self.config['Registration']['year']
    
    @property
    def birth_month(self):
        return self.config['Registration']['month']
    
    @property
    def birth_day(self):
        return self.config['Registration']['day']
    
    @property
    def isnongli(self):
        return self.config['Registration']['isnongli']
    
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
    def ruokuai(self):
        return self.config['ruokuai']['ruokuai']
    
    @property
    def rk_user(self):
        return self.config['ruokuai']['rk_user']
    
    @property
    def rk_pass(self):
        return self.config['ruokuai']['rk_pass']
    
    @property
    def admin_name(self):
        return self.config['admin']['admin_name']
    
    @property
    def admin_pass(self):
        return self.config['admin']['admin_pass']
    

if __name__ == '__main__':
    pass
    
