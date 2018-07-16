#!/usr/bin/python

import os
import re
from Utils import *

class ToolEnv:
	def initToolEnv(self, name):
		ToolEnv.__info = {}
		ToolEnv.__info['name'] = name
		info = getADUser(name, '')
		ToolEnv.__info['mail'] = info[0][1]['mail'][0]
		ToolEnv.__info['tel'] = info[0][1]['telephoneNumber'][0]
		ToolEnv.__info['fullname'] = info[0][1]['displayName'][0]

	def getUserName(self):
		return ToolEnv.__info['name']

	def getUserFullName(self):
		return ToolEnv.__info['fullname']

	def getUserMail(self):
		return ToolEnv.__info['mail']

	def getUserTel(self):
		return ToolEnv.__info['tel']
