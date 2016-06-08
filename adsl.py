#!/usr/bin/env python3

'''ADSL redial
'''

# from http://www.cnblogs.com/misoag/archive/2013/01/08/2851438.html

import os
g_adsl_account = {"name": "adsl",
				"username": "0512...",
				"password": "..."}

	
class Adsl(object):
	#==============================================================================
	# __init__ : name: adsl名称
	#==============================================================================
	def __init__(self, name='adsl', user='', password=''):
		self.name = name
		self.username = user
		self.password = password

		
	#==============================================================================
	# set_adsl : 修改adsl设置
	#==============================================================================
	def set_adsl(self, account):
		self.name = account["name"]
		self.username = account["username"]
		self.password = account["password"]

	
	#==============================================================================
	# connect : 宽带拨号
	#==============================================================================
	def connect(self):
		cmd_str = "rasdial %s %s %s" % (self.name, self.username, self.password)
		os.system(cmd_str)
		time.sleep(5)

		
	#==============================================================================
	# disconnect : 断开宽带连接
	#==============================================================================
	def disconnect(self):
		cmd_str = "rasdial %s /disconnect" % self.name
		os.system(cmd_str)
		time.sleep(5)

	
	#==============================================================================
	# reconnect : 重新进行拨号
	#==============================================================================
	def reconnect(self):
		self.disconnect()
		self.connect()

