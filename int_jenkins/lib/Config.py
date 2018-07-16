#!/usr/bin/python

import sys
import os
import re
import getpass

class Config:
	__confdict = {'ask':'0', 'showkey':'yes', 'configfile':''}
	module = None

	def __init__(self, module=None):
		self.module = module

	def addFromArg(self, arglist):
		if len(arglist) % 2 != 0:
			print "Error: arg number should be even"
			sys.exit(1)
		for i in range(len(arglist)/2):
			if arglist[i*2][0] != '-':
				print "Error: arg "+ arglist[i*2]
				sys.exit(1)
			elif arglist[i*2+1][0] == '-':
				print "Error: arg "+ arglist[i*2+1]
				sys.exit(1)
			else:
				if arglist[i*2][1:] != 'nokey':
					Config.__confdict[arglist[i*2][1:]] = arglist[i*2+1]
		if Config.__confdict['configfile']:
			loadConfigFromFile(argDict['configfile'])

	def loadConfigFromFile(self, fileName, override=False):
		fileConfig = open(fileName, 'r')
		for line in fileConfig.readlines():
			line.strip()
			line = re.sub('#.*', '', line)
			itemList = re.split('=', line, 1)
			if len(itemList) == 2:
				key,value = itemList
				key = key.strip()
				value = value.strip()
				if value[-1] == '!':
					value = value[:-1].strip()
					force = True
				else:
					force = False
				if force == True or override == True or key not in Config.__confdict.keys():
					if key != 'nokey':
						Config.__confdict[key] = value
		fileConfig.close()

	def __checkInLineConf(self, value):
		if value != '':
			valList = re.split('\^', value)
			for oneVal in valList[1:]:
				askList = re.split('\s*=\s*', oneVal.strip(), 1)
				if len(askList) > 1:
					key = askList[0].strip()
					if self.module and key != 'ask' and key != 'nokey':
						key = self.module+'.'+key
					if key != 'nokey':
						Config.__confdict[key] = askList[1].strip()
			return valList[0].strip()
		else:
			return value

	def __checkInputValue(self, value, pattern):
		if pattern:
			if re.match(pattern, value):
				return True
			else:
				return False
		else:
			if value != '':
				return True
			else:
				return False

	def __saveItemToFile(self, itemKey, itemValue, fileName):
		tmpConfigDict = {}
		if os.path.isfile(fileName):
			fileConfig = open(fileName, 'r')
			for line in fileConfig.readlines():
				line.strip()
				line = re.sub('#.*', '', line)
				itemList = re.split('=', line, 1)
				if len(itemList) == 2:
					key,value = itemList
					key = key.strip()
					value = value.strip()
					if value[-1] == '!':
						value = value[:-1].strip()
					if key != 'nokey':
						tmpConfigDict[key] = value
			fileConfig.close()
		tmpConfigDict[itemKey] = itemValue
		fileConfig = open(fileName, 'w+')
		for key,value in tmpConfigDict.items():
			fileConfig.write('%s = %s\n' % (key, value))
		fileConfig.close()
		return itemValue

	def getConf(self, key, prompt, default='', ask=None, save=None, echo=True, maxask=3):
		if self.module and key != 'ask' and key != 'nokey':
			key = self.module+'.'+key

		if Config.__confdict['showkey'] == 'yes':
			showKey = '('+key+') '
		else:
			showKey = ''

		match = re.search('<\s*([\w\|]+)\s*>$', prompt)
		if match:
			rangeList = match.group(1).split('|')
		else:
			rangeList = []

		regMatch = re.search('{(.+)}$', prompt)
		if regMatch:
			pattern = regMatch.group(1)
		else:
			pattern = None

		if ask:
			ask = str(ask)
		else:
			ask = Config.__confdict['ask']

		if ask == '0':
			if key in Config.__confdict:
				if save:
					self.__saveItemToFile(key, Config.__confdict[key], save)
				return Config.__confdict[key]
			elif default != '':
				if key != 'nokey':
					Config.__confdict[key] = default
				if save:
					self.__saveItemToFile(key, default, save)
				return default
			else:
				while True:
					if maxask <= 0:
						print "\nArg error. Exit ..."
						sys.exit(1)
					maxask -= 1
					sys.stdout.write('%s%s : ' % (showKey, prompt))
					value = self.__checkInLineConf(sys.stdin.readline().strip() if echo else getpass.getpass('').strip())
					if match:
						if value in rangeList:
							break
					else:
						if self.__checkInputValue(value, pattern):
							break
				if key != 'nokey':
					Config.__confdict[key] = value
				if save:
					self.__saveItemToFile(key, value, save)
				return value
		elif ask == '1':
			if key in Config.__confdict:
				return Config.__confdict[key]
			elif default != '':
				while True:
					if maxask <= 0:
						print "Arg err. Exit ..."
						sys.exit(1)
					maxask -= 1
					sys.stdout.write('%s%s [%s]: ' % (showKey, prompt, default))
					value = self.__checkInLineConf(sys.stdin.readline().strip() if echo else getpass.getpass('').strip())
					if value == '':
						value = default
					if match:
						if value in rangeList:
							break
					else:
						if self.__checkInputValue(value, pattern):
							break
				if key != 'nokey':
					Config.__confdict[key] = value
				if save:
					self.__saveItemToFile(key, value, save)
				return value
			else:
				while True:
					if maxask <= 0:
						print "Arg err. Exit ..."
						sys.exit(1)
					maxask -= 1
					sys.stdout.write('%s%s : ' % (showKey, prompt))
					value = self.__checkInLineConf(sys.stdin.readline().strip() if echo else getpass.getpass('').strip())
					if match:
						if value in rangeList:
							break
					else:
						if self.__checkInputValue(value, pattern):
							break
				if key != 'nokey':
					Config.__confdict[key] = value
				if save:
					self.__saveItemToFile(key, value, save)
				return value
		else:
			if key in Config.__confdict:
				default = Config.__confdict[key]
			if default != '':
				while True:
					if maxask <= 0:
						print "Arg err. Exit ..."
						sys.exit(1)
					maxask -= 1
					sys.stdout.write('%s%s [%s]: ' % (showKey, prompt, default))
					value = self.__checkInLineConf(sys.stdin.readline().strip() if echo else getpass.getpass('').strip())
					if value == '':
						value = default
					if match:
						if value in rangeList:
							break
					else:
						if self.__checkInputValue(value, pattern):
							break
				if key != 'nokey':
					Config.__confdict[key] = value
				if save:
					self.__saveItemToFile(key, value, save)
				return value
			else:
				while True:
					if maxask <= 0:
						print "Arg err. Exit ..."
						sys.exit(1)
					maxask -= 1
					sys.stdout.write('%s%s : ' % (showKey, prompt))
					value = self.__checkInLineConf(sys.stdin.readline().strip() if echo else getpass.getpass('').strip())
					if match:
						if value in rangeList:
							break
					else:
						if self.__checkInputValue(value, pattern):
							break
				if key != 'nokey':
					Config.__confdict[key] = value
				if save:
					self.__saveItemToFile(key, value, save)
				return value

	def dumpConf(self):
		return Config.__confdict

	def dumpConfPretty(self):
		strDump = 'Config:\n'
		for (key, var) in Config.__confdict.items():
			strDump += '    %s => %s\n' % (key, var)
		strDump += '\nCurrent dir: %s\n' % os.getcwd()
		return strDump
