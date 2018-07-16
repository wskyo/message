#!/usr/bin/python
#Filename:Utils.py
import re
import os
import sys
import ldap
import smtplib
import pexpect
import tempfile
from email.mime.text import MIMEText
import multiprocessing
import time
import urllib
import re

__defaultLogFile = ''
__notifyList = []
__dirStack = []
__multiRunErrMsgList = []
intToolsUtilsMultiRunErrMsgQueue = None

def setDefaultLogFile(fileName):
	global __defaultLogFile
	__defaultLogFile = fileName

def getDefaultLogFile():
	global __defaultLogFile
	return __defaultLogFile

def addNotifyInfo(strNotify, addHead = False):
	global __notifyList
	if addHead:
		__notifyList.insert(0, strNotify)
	else:
		__notifyList.append(strNotify)

def getNotifyInfo():
	global __notifyList
	return '\n==========================================================================\n\n'.join(__notifyList)

class __bothLog(file):
	def __init__(self, filename, mode, noprint):
		self.notify = []
		self.filename = filename
		self.__noprint = noprint
		if len(self.filename) > 0:
			file.__init__(self, self.filename, mode)
	def write(self, s):
		if len(self.filename) > 0:
			file.write(self, s)
		if not self.__noprint:
			sys.stdout.write(s)
		self.notify.append(s)
		while len(self.notify) > 200:
			self.notify.pop(0)
	def flush(self):
		if len(self.filename) > 0:
			file.flush(self)
	def close(self):
		if len(self.filename) > 0:
			file.close(self)
	def getNotify(self):
		return ''.join(self.notify)

def chdir(path, log='', noprint=False):
	oldDir = os.getcwd()
	if len(log) == 0:
		log = getDefaultLogFile()
	logFile = __bothLog(log, 'a', noprint)
	logFile.write('chdir: %s => %s\n' % (oldDir, path))
	os.chdir(path)
	return oldDir

def pushdir(path, log=''):
	global __dirStack
	oldDir = chdir(path, log)
	__dirStack.insert(0, oldDir)
	return oldDir

def popdir(log=''):
	global __dirStack
	oldDir = ''
	if len(__dirStack) > 0:
		oldDir = chdir(__dirStack[0], log)
		__dirStack = __dirStack[1:]
	return oldDir

def checkDir(path):
	if not os.path.isdir(path):
		docmd('rm -rf '+path)
		docmd('mkdir -p '+path)

def getToolPath():
	return re.sub('lib$', '', os.path.dirname(__file__), 1)

def docmd(cmd, log='', exp={}, noprint=False):
	if len(log) == 0:
		log = getDefaultLogFile()
	logFile = __bothLog(log, 'a', noprint)
	logFile.write('docmd:'+os.getcwd()+'$ '+cmd+'\n')
	ask,answer = [],[]
	for key,val in exp.items():
		ask.append(key)
		answer.append(val)
	ask.append(pexpect.EOF)
	answer.append(None)
	proc = pexpect.spawn('/bin/bash', ['-c', cmd], timeout=None, logfile=logFile)
	proc.setecho(False)
	while True:
		index = proc.expect(ask)
		if ask[index] == pexpect.EOF:
			break
		else:
			if answer[index]:
				proc.sendline(answer[index])
			else:
				proc.sendline()
	proc.close()
	if proc.exitstatus == 0:
		logFile.close()
	else:
		logFile.write("Error: docmd:%s$ %s <Return %d>\n" % (os.getcwd(), cmd, proc.exitstatus))
		logFile.close()
		notifyStr = logFile.getNotify()
		addNotifyInfo(notifyStr)
		global intToolsUtilsMultiRunErrMsgQueue
		if intToolsUtilsMultiRunErrMsgQueue:
			intToolsUtilsMultiRunErrMsgQueue.put(notifyStr)
		sys.exit(1)

def docmd_noexit(cmd, log='', exp={}, noprint=False):
	if len(log) == 0:
		log = getDefaultLogFile()
	logFile = __bothLog(log, 'a', noprint)
	logFile.write('docmd_noexit:'+os.getcwd()+'$ '+cmd+'\n')
	ask,answer = [],[]
	for key,val in exp.items():
		ask.append(key)
		answer.append(val)
	ask.append(pexpect.EOF)
	answer.append(None)
	proc = pexpect.spawn('/bin/bash', ['-c', cmd], timeout=None, logfile=logFile)
	proc.setecho(False)
	while True:
		index = proc.expect(ask)
		if ask[index] == pexpect.EOF:
			break
		else:
			if answer[index]:
				proc.sendline(answer[index])
			else:
				proc.sendline()
	proc.close()
	if proc.exitstatus == 0:
		logFile.close()
	else:
		logFile.write("Error: docmd_noexit:%s$ %s <Return %d>\n" % (os.getcwd(), cmd, proc.exitstatus))
		logFile.close()
		notifyStr = logFile.getNotify()
		addNotifyInfo(notifyStr)
		global intToolsUtilsMultiRunErrMsgQueue
		if intToolsUtilsMultiRunErrMsgQueue:
			intToolsUtilsMultiRunErrMsgQueue.put(notifyStr)
	return proc.exitstatus

def docmd_forever(cmd, log='', exp={}, noprint=False):
	if len(log) == 0:
		log = getDefaultLogFile()
	logFile = __bothLog(log, 'a', noprint)
	logFile.write('docmd_forever:'+os.getcwd()+'$ '+cmd+'\n')
	ask,answer = [],[]
	for key,val in exp.items():
		ask.append(key)
		answer.append(val)
	ask.append(pexpect.EOF)
	answer.append(None)
	while True:
		proc = pexpect.spawn('/bin/bash', ['-c', cmd], timeout=None, logfile=logFile)
		proc.setecho(False)
		while True:
			index = proc.expect(ask)
			if ask[index] == pexpect.EOF:
				break
			else:
				if answer[index]:
					proc.sendline(answer[index])
				else:
					proc.sendline()
		proc.close()
		if proc.exitstatus == 0:
			logFile.close()
			break
		else:
			logFile.write("Error: docmd_forever:%s$ %s <Return %d>, try again\n" % (os.getcwd(), cmd, proc.exitstatus))

def getADUser(user, key):
	print '---------------------------'
	print user
	# Set debugging level
	hostip='10.128.161.26'
	hostuser='CN=gcquery,CN=Users,DC=ta-mp,DC=com'
	hostpwd='Gc123456'
	base = "OU=SHANGHAI,DC=cn,DC=ta-mp,DC=com"
	res=[]
	scope = ldap.SCOPE_SUBTREE
	# Set debugging level
	ldap.set_option(ldap.OPT_DEBUG_LEVEL,0)
	ldapmodule_trace_level = 1
	ldapmodule_trace_file = sys.stderr
	filter = '(&(objectClass=person)(sAMAccountName=%s))' % user

	# Create LDAPObject instance
	ldapobj = ldap.initialize('ldap://%s' %hostip)

	# Set LDAP protocol version used
	ldapobj.protocol_version=ldap.VERSION3
	# Try a bind to provoke failure if protocol version is not supported
	ldapobj.simple_bind_s(hostuser, hostpwd)

	#get the ldap infomation user the user and key
	if cmp('', key)==0:
		res = ldapobj.search_ext_s(base, scope, filter)
	else:
		tempres = ldapobj.search_ext_s(base, scope, filter, attrlist = [key])
		if(len(tempres)==0):
			return res
		res=return_result(tempres)
		#print_result(res)

	# Close connection
	ldapobj.unbind_s()

	return res

def getADUserByMail(mail, key=''):
	# Set debugging level
	hostip='10.128.161.26'
	hostuser='CN=Rongbin XUE,OU=SDD,OU=SHANGHAI,DC=cn,DC=ta-mp,DC=com'
	hostpwd='Aa123456'
	base = "OU=SHANGHAI,DC=cn,DC=ta-mp,DC=com"
	res=[]
	scope = ldap.SCOPE_SUBTREE
	# Set debugging level
	ldap.set_option(ldap.OPT_DEBUG_LEVEL,0)
	ldapmodule_trace_level = 1
	ldapmodule_trace_file = sys.stderr
	filter = '(&(objectClass=person)(mail=%s))' % mail

	# Create LDAPObject instance
	ldapobj = ldap.initialize('ldap://%s' %hostip)

	# Set LDAP protocol version used
	ldapobj.protocol_version=ldap.VERSION3
	# Try a bind to provoke failure if protocol version is not supported
	ldapobj.simple_bind_s(hostuser, hostpwd)

	#get the ldap infomation user the user and key
	if cmp('', key)==0:
		res = ldapobj.search_ext_s(base, scope, filter)
	else:
		tempres = ldapobj.search_ext_s(base, scope, filter, attrlist = [key])
		if(len(tempres)==0):
			return res
		res=return_result(tempres)
		#print_result(res)

	# Close connection
	ldapobj.unbind_s()

	return res

def return_result(search_result):
        for n in range(len(search_result)):
		for attr in search_result[n][1].keys():
			for i in range(len(search_result[n][1][attr])):
				#print repr(search_result[n][1][attr][0])
				#print search_result[n][1][attr]

				#the passwd infomation repr()
				#print "%s: %s" % (attr, repr(search_result[n][1][attr][i]))
				
				#temppm="%s: %s" % (attr, search_result[n][1][attr][i])
				returnval=[attr,search_result[n][1][attr][i]]
				return returnval

def getADUserProf(user, key):
	return getADUser(user, key)[1]

###get mail list user this method, from urllist
def getMailListUserUrllib(listName, smtpAddrSet):
	##open url 
	url='http://maillist.tclmobile.cn/cgi-bin/mailman/roster/' + listName
	html = urllib.urlopen(url).read()
	##release message
	m = re.findall(r"<li><a href=(.*)>(.*)</a>", html)
	if len(m) != 0 and smtpAddrSet != None:
		for n in range(len(m)):	
			tmpstr = m[n][1]
		        tmp = tmpstr.replace(' at ','@')
		        tmp = '<' + tmp + '>'
			#print tmp
		        smtpAddrSet.add(tmp)
	else:
		pass

###read file and return key-value
def readFile(splittag, filePath='', fileType='rU'):
	file_obj = None
	dic = {}
	if filePath != '':
		file_obj = open(filePath, fileType)
		file_lines = file_obj.readlines()
		for line in file_lines:
			line.strip()
			key = ''
			value = ''
			if line != None and line.__contains__(splittag):
				key = line.split(splittag)[0]
				value = line.split(splittag)[1]
			if key != '' and value != '':
				dic[key]=value
	if file_obj != None:
		file_obj.close()
	return dic


def textMail(sender, tolist, subject, content):
	msg = MIMEText(content)
	msg['Subject'] = subject
	fromAdd = getADUserProf(sender, 'mail')
	msg['From'] = getADUserProf(sender, 'displayName') + ' <' + fromAdd + '>'
	tos = []
	for to in tolist:
		match = re.search('<([^<>@]+@[^<>@]+)>', to)
		if match:
			msg['To'] = to.strip()
			tos.append(match.group(1))
		else:
			toAdd = getADUserProf(to, 'mail')
			msg['To'] = getADUserProf(to, 'displayName') + ' <' + toAdd + '>'
			tos.append(toAdd)
	s = smtplib.SMTP('mailsz.jrdcom.com')
	s.sendmail(fromAdd, tos, msg.as_string())
	s.quit()

def clone(path, server):
	chdir(path)
	docmd('rm -rf .repo .git')
	tmpstr = tempfile.mkdtemp('HAPPYBUILD', 'temp', '/tmp/')
	tmpstr = tmpstr + '/'
	chdir(tmpstr)
	docmd('git clone '+server)
	return os.getcwd()

def push(path):
	chdir(path)
	docmd('git pull')
	docmd('git push')

class MultiRun:
	def __init__(self):
		global intToolsUtilsMultiRunErrMsgQueue
		intToolsUtilsMultiRunErrMsgQueue = multiprocessing.Queue()
		self.procList = []
		self.errMsgList = []
	def add(self, task, *argList):
		proc = multiprocessing.Process(target=task, args=argList)
		self.procList.append(proc)
	def run(self):
		retVal = 0
		global intToolsUtilsMultiRunErrMsgQueue
		global __multiRunErrMsgList
		for proc in self.procList:
			proc.start()
		isRunning = True
		while isRunning:
			isRunning = False
			time.sleep(2)
			for proc in self.procList:
				if proc.is_alive():
					isRunning = True
				else:
					if proc.exitcode != 0:
						retVal = 1
						for p in self.procList:
							if p.is_alive():
								p.terminate()
		while not intToolsUtilsMultiRunErrMsgQueue.empty():
			tmpMsg = intToolsUtilsMultiRunErrMsgQueue.get()
			self.errMsgList.append(tmpMsg)
			__multiRunErrMsgList.append(tmpMsg)
		for proc in self.procList:
			proc.join()
		return retVal
	def getErrMsgList(self):
		return self.errMsgList

def getErrMsgList():
	global __multiRunErrMsgList
	return __multiRunErrMsgList

if __name__=='__main__':
        username=sys.argv[1]
        keyval=sys.argv[2]
        listmap=getADUser(username, keyval)
        print type(listmap)
        for x in listmap:
            print x
#end of model
