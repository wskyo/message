#!/usr/bin/python

import os
import re
from Utils import *

class UserInfo:
	def initUserInfo(self, name):
		name = name.strip()
		UserInfo.__info = {}

		if re.search('#$', name):
			name = name[:-1].strip()
			for line in file('%s/lib/passwd' % getToolPath()):
				if re.match('^\s*#', line):
					continue
				infoList = line.split(':')
				if infoList[0].strip() == name:
					UserInfo.__info['name'] = name
					UserInfo.__info['mail'] = infoList[1].strip()
					UserInfo.__info['tel'] = infoList[2].strip()
					UserInfo.__info['fullname'] = infoList[3].strip()
					UserInfo.__info['mailserver'] = infoList[4].strip()
			name = UserInfo.__info['name']
		else:
			UserInfo.__info['name'] = name
			info = getADUser(name, '')
			UserInfo.__info['mail'] = info[0][1]['mail'][0]
			if 'telephoneNumber' in info[0][1].keys():
				UserInfo.__info['tel'] = info[0][1]['telephoneNumber'][0]
			else:
				UserInfo.__info['tel'] = 'N/A'
			UserInfo.__info['fullname'] = info[0][1]['displayName'][0]
			UserInfo.__info['mailserver'] = 'mail.tcl.com'

	def getName(self):
		return UserInfo.__info['name']

	def getFullName(self):
		return UserInfo.__info['fullname']

	def getMail(self):
		return UserInfo.__info['mail']

	def getTel(self):
		return UserInfo.__info['tel']

	def getMailServer(self):
		return UserInfo.__info['mailserver']
