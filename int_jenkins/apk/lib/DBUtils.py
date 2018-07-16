#!/usr/bin/python
############################################################################
## DB Utils for connection datebase and update PR status from browser.
## add by jianbo.deng for superspam create 2013-08-28
############################################################################
import MySQLdb
from time import strftime, localtime
import datetime
import time
import mechanize
import re
import sys
import os
from Utils import *
from Config import *
from UserInfo import *

class DBUtils:
	needDeliverPR = ''
	isLogedInBugzilla = False
	cloneBugs = []
	bygForCirle = []
	br = mechanize.Browser()
	br.set_handle_robots(False)
	br.set_handle_equiv(False)
	##  begin modify by laiyinfang 2014-04-16
	def getVeriSWOldResolveInfoDict(self, mysqlConn, oneProductIdNum, prVeriSWOldResolveInfoDict, prResolveFromBugzillaInfoDict,curVerTimeStr, lastVerTimeStr):
		## end modily by laiyinfang 2014-04-16
		productIdSqlList = []
		oneProductIdNumInt = self.getIDNumberAndCodeList(oneProductIdNum, mysqlConn)
		productIdSqlList.append('product_id=%d' % int(oneProductIdNumInt))
		if curVerTimeStr:
			mysqlCursor = mysqlConn.cursor()
			mysqlCursor.execute('SELECT bug_id,bug_type,reporter,bug_status,function_id,target_milestone,short_desc,cf_comment_cea,assigned_to,resolution,component_id,priority,cf_ipr,deadline FROM bugs WHERE bug_status="VERIFIED_SW" AND (resolution="Validated" OR resolution="Can\'t test") AND (%s)' % ' OR '.join(productIdSqlList))
			while True:
				resList = mysqlCursor.fetchone()
				if not resList:
					break
				name = ''						
				name = self.getCompNameFromUid(resList[10],mysqlConn)
				bugid = resList[0]
				if self.appname in self.prVeriSWFromCodeInfoDict.keys():
					if bugid in self.prVeriSWFromCodeInfoDict[self.appname].keys():
						continue				
				tmpCursor = mysqlConn.cursor()
				tmpCursor.execute('SELECT bug_when FROM bugs_activity WHERE bug_id=%d AND added="VERIFIED_SW" ORDER BY bug_when DESC' % bugid)
				tmpResList = tmpCursor.fetchone()
				if tmpResList:
					match=re.match('(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+)', curVerTimeStr)
					if datetime.datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), int(match.group(5)), int(match.group(6))) < tmpResList[0]:
						##begin add by laiyinfang 2014-04-16
						prResolveFromBugzillaInfoDict[bugid] = {}
						prResolveFromBugzillaInfoDict[bugid]['type'] = resList[1]
						prResolveFromBugzillaInfoDict[bugid]['reporter'] = self.getUserNameFromUid(resList[2], mysqlConn)
						prResolveFromBugzillaInfoDict[bugid]['status'] = resList[3]
						prResolveFromBugzillaInfoDict[bugid]['ownerinfo'] = self.getOwnerInfo(bugid, lastVerTimeStr, curVerTimeStr, mysqlConn, resList[8])
						prResolveFromBugzillaInfoDict[bugid]['function'] = self.getFunctionName(resList[4], mysqlConn)
						prResolveFromBugzillaInfoDict[bugid]['milestone'] = resList[5]
						prResolveFromBugzillaInfoDict[bugid]['desc'] = resList[6]
						prResolveFromBugzillaInfoDict[bugid]['commentcea'] = resList[7]
						prResolveFromBugzillaInfoDict[bugid]['priority'] = resList[11]
						prResolveFromBugzillaInfoDict[bugid]['ipr'] = resList[12]
						if not resList[13]:
							prResolveFromBugzillaInfoDict[bugid]['deadline'] = ''
						else:
							prResolveFromBugzillaInfoDict[bugid]['deadline'] = resList[13]
						prResolveFromBugzillaInfoDict[bugid]['localpath'] = ''
						prResolveFromBugzillaInfoDict[bugid]['impact'] =''
						prResolveFromBugzillaInfoDict[bugid]['suggestion'] = ''
						prResolveFromBugzillaInfoDict[bugid]['persoregen'] = 'Unknown'
						prResolveFromBugzillaInfoDict[bugid]['component'] = name
						##end add by laiyinfang 2014-04-16
						continue
				else:
					continue
				tmpCursor.close()
				prVeriSWOldResolveInfoDict[bugid] = {}
				prVeriSWOldResolveInfoDict[bugid]['type'] = resList[1]
				prVeriSWOldResolveInfoDict[bugid]['reporter'] = self.getUserNameFromUid(resList[2], mysqlConn)
				prVeriSWOldResolveInfoDict[bugid]['status'] = resList[3]
				prVeriSWOldResolveInfoDict[bugid]['ownerinfo'] = self.getOwnerInfo(bugid, lastVerTimeStr, curVerTimeStr, mysqlConn, resList[8])
				prVeriSWOldResolveInfoDict[bugid]['function'] = self.getFunctionName(resList[4], mysqlConn)
				prVeriSWOldResolveInfoDict[bugid]['milestone'] = resList[5]
				prVeriSWOldResolveInfoDict[bugid]['desc'] = resList[6]
				prVeriSWOldResolveInfoDict[bugid]['commentcea'] = resList[7]
				prVeriSWOldResolveInfoDict[bugid]['priority'] = resList[11]
				prVeriSWOldResolveInfoDict[bugid]['ipr'] = resList[12]
				if not resList[13]:
					prVeriSWOldResolveInfoDict[bugid]['deadline'] = ''
				else:
					prVeriSWOldResolveInfoDict[bugid]['deadline'] = resList[13]
				prVeriSWOldResolveInfoDict[bugid]['impact'] = ''
				prVeriSWOldResolveInfoDict[bugid]['suggestion'] = ''
				prVeriSWOldResolveInfoDict[bugid]['persoregen'] = 'Unknown'
				prVeriSWOldResolveInfoDict[bugid]['component'] = name
				self.needDeliverPR = True
			mysqlCursor.close()
			

	def getUserNameFromUid(self, uid, mysqlConn):
		cur = mysqlConn.cursor()
		cur.execute('SELECT realname,login_name FROM profiles WHERE userid=%s' % str(uid))
		res = cur.fetchone()
		userName = '%s <%s>' % (res[0], res[1])
		cur.close()
		return userName
	def getCompNameFromUid(self, uid, mysqlConn):
		cur = mysqlConn.cursor()
		cur.execute('SELECT name FROM components WHERE id =%d' % int(uid))
		res = cur.fetchone()
		compName = res[0]
		cur.close()
		return compName

	def getOwnerInfo(self, bugid, lastVerTimeStr, curVerTimeStr, mysqlConn, assigned_to):
		conf = Config()
		if not lastVerTimeStr:
			#lastVerTimeStr = conf.getConf('projectlaunchtime', 'Project launch time')
			lastVerTimeStr = "1970-01-01 00:00:00"
		if not curVerTimeStr:
			curVerTimeStr = datetime.date.today().strftime('%Y-%m-%d %H:%M:%S')
		cur = mysqlConn.cursor()
		cur.execute('SELECT who,bug_when FROM bugs_activity WHERE bug_id=%d AND bug_when>"%s" AND bug_when<"%s" AND (added="RESOLVED" OR added="DELIVERED") ORDER BY bug_when DESC'% (bugid, lastVerTimeStr, curVerTimeStr))
		resolvList = cur.fetchall()
		cur.close()
		tmpList = []
		nCount = 0
		for resolve in resolvList:
			nCount += 1
			tmpList.append('%d) %s [%s]' % (nCount, self.getUserNameFromUid(resolve[0], mysqlConn), resolve[1]))
		if tmpList:
			return '\r\n'.join(tmpList)
		else:
			return '1) %s []' % self.getUserNameFromUid(assigned_to, mysqlConn)

	def getFunctionName(self, funcId, mysqlConn):
		cur = mysqlConn.cursor()
		cur.execute('SELECT name FROM functions WHERE id=%s' % str(funcId))
		funcName = cur.fetchone()[0]
		cur.close()
		return funcName

	def deliverPRlist(self, conf, mysqlConn, prVeriSWOldResolveInfoDict,prResolveFromBugzillaInfoDict):		
		if self.needDeliverPR :
			appBugs={}			
			for bugid,buginfo in prVeriSWOldResolveInfoDict.items():
				if re.search('\[\s*'+ self.bugzillaAppName,buginfo['desc'],re.I) or re.search('\[\s*'+self.bugzillaAppNameTwo,buginfo['desc'],re.I) or re.search(self.bugzillaAppName,buginfo['component'],re.I) or re.search(self.bugzillaAppNameTwo,buginfo['component'],re.I):
					print "veri sw old resovle pr ------ %s" % bugid
					if buginfo['status'] in ['VERIFIED_SW', 'DELIVERED']:
						if self.appname not in self.prNeedDelivHash.keys():
							self.prNeedDelivHash[self.appname] = {}
						self.prNeedDelivHash[self.appname][bugid] = [buginfo['status'], buginfo['milestone']]
						
						appBugs[bugid] = buginfo
						appBugs[bugid]['status'] = 'DELIVERED'
			if self.appname in self.prVeriSWFromCodeInfoDict.keys():
				for bugid,buginfo in self.prVeriSWFromCodeInfoDict[self.appname].items():				
					print "veri sw resovle pr ------ %s" % bugid
					if buginfo['status'] in ['VERIFIED_SW', 'DELIVERED']:
						if self.appname not in self.prNeedDelivHash.keys():
							self.prNeedDelivHash[self.appname] = {}
						self.prNeedDelivHash[self.appname][bugid] = [buginfo['status'], buginfo['milestone']]	
						appBugs[bugid] = buginfo
						appBugs[bugid]['status'] = 'DELIVERED'
			if appBugs:	
				self.apkDeliveredBugs[self.appname] = appBugs.copy()
			appBugs = {}

			

		noNeedDeliveredBugs = {}
		for bugid,buginfo in prResolveFromBugzillaInfoDict.items():
			if re.search('\[\s*'+ self.bugzillaAppName,buginfo['desc'],re.I) or re.search('\[\s*'+ self.bugzillaAppNameTwo,buginfo['desc'],re.I) or re.search(self.bugzillaAppName,buginfo['component'],re.I) or re.search(self.bugzillaAppNameTwo,buginfo['component'],re.I):
				print "veri sw old resovle from buzilla no need delivered pr ------ %s" % bugid, buginfo['milestone']				
				noNeedDeliveredBugs[bugid] = buginfo
		if self.appname in self.prResolveFromCodeInfoDict.keys():
			for bugid,buginfo in self.prResolveFromCodeInfoDict[self.appname].items():				
				print "veri sw old resovle from code  no need delivered pr ------ %s" % bugid, buginfo['milestone']
				noNeedDeliveredBugs[bugid] = buginfo
		if noNeedDeliveredBugs:	
			self.apkSWNoDeliveredBugs[self.appname] = noNeedDeliveredBugs.copy()
		noNeedDeliveredBugs = {}	
		mysqlConn.close()		 


	### deliver PR status from browser user mechanize
	def deliverPR(self, conf, prHash,version):
		countPRNeedDeliver = 0
		curPRDeliverNumber = 1
		bugzillaloginname = 'hz.int'
		bugzillapassword = 'ptc'
		for pr,infoList in prHash.items():
			if infoList[0] in ['VERIFIED_SW', 'DELIVERED']:
				countPRNeedDeliver += 1
		print 'CAUTION: %d PRs are to be delivered or be added comment' % countPRNeedDeliver
		for pr,infoList in prHash.items():
			if infoList[0] in ['VERIFIED_SW', 'DELIVERED']:
				if not self.isLogedInBugzilla:
					while True:
						if not bugzillaloginname and not bugzillapassword:
							bugzillaloginname = conf.getConf('bugzillaloginname', 'Bugzilla loggin name', ask=2)
							bugzillapassword = conf.getConf('bugzillapassword', 'Bugzilla password', ask=2, echo=False)
						self.br.open('http://bugzilla.tcl-ta.com/index.cgi?GoAheadAndLogIn=1')
						self.br.select_form(name='login')
						self.br['Bugzilla_login'] = bugzillaloginname
						self.br['Bugzilla_password'] = bugzillapassword
						resp = self.br.submit()
						if re.search('Welcome\sto\sBugzilla!', resp.get_data()):
							print "Login bugzilla ok"
							break
						else:
							print "Login bugzilla fail, try again..."
					self.isLogedInBugzilla = True
				try:
					self.br.open('http://bugzilla.tcl-ta.com/show_bug.cgi?id=%s' % str(pr))
					print '%d) Deliver PR %s : %s' % (curPRDeliverNumber, str(pr), self.br.title())
					curPRDeliverNumber += 1
					response = self.br.response()
					#Python mechanize is broken, fixing it.
					response.set_data(response.get_data().replace("<br/>", "<br />")) 
					self.br.set_response(response)
					self.br.select_form(name='changeform')
					if infoList[0] == 'VERIFIED_SW':
						self.br['knob'] = ['deliver']
					#version = conf.getConf('version','current version')
					verstr = 'v%s' % version
					fullName = conf.getConf('bugzillaloginname', 'Bugzilla loggin name', 'hudson.admin')
					comment = 'The new ref is updated by %s with int tool superspam\n' % fullName
					if infoList[0] == 'VERIFIED_SW':
						comment += 'Change bug status to DELIVERED\n'						
					comment += 'New ref: %s' % verstr
					comment += '\nPlease use %s to verify' % verstr
					self.br['comment'] = comment
					if infoList[0] == 'VERIFIED_SW':
						milestone = infoList[1]
						if not re.search('\s%s\s' % verstr, milestone) and not re.search('\s%s$' % verstr, milestone):
							self.br['target_milestone'] = verstr
						#br['target_milestone'] = milestone
					self.br.submit()
				except:
					print 'WARNING: Deliver PR %s fail, please check' % str(pr)
					
			else:
				pass

	def mechanizeClose(self):
		self.br.close()

	def getIDNumberAndCodeList(self, productIdStr, mysqlConn):		
		if not re.match('\d+', productIdStr):
			mysqlCursor = mysqlConn.cursor()
			mysqlCursor.execute('SELECT id FROM products WHERE name="%s"' % productIdStr)
			productIdNumStr = str(mysqlCursor.fetchone()[0])
			mysqlCursor.close()
		else:
			productIdNumStr = productIdStr
		return productIdNumStr


	def getPrFromCodeListForOneApk(self, bugid, appname):		
		mysqlCursor = self.mysqlConn.cursor()
		mysqlCursor.execute('SELECT product_id FROM bugs WHERE bug_id=%d' % bugid)
		resList = mysqlCursor.fetchone()			
		oneProductIdNum	= self.AlmCheckDict[appname]['apkproject']
		oneProductIdNumInt = self.getIDNumberAndCodeList(oneProductIdNum, self.mysqlConn)	
		if resList:
			curBugProductId = resList[0]
			if int(curBugProductId) == int(oneProductIdNumInt):				
				return True
			else:
				return False
		else:
			return False
		mysqlCursor.close()

		## get VERIFIED_SW and RESOLVED PR 
	def getSWAndRelPRList(self, conf, mysqlConn, curVerTimeStr, lastVerTimeStr):
		if self.appname in self.prFromCodeDict.keys():		
			for bugid in self.prFromCodeDict[self.appname].keys():
				mysqlCursor = mysqlConn.cursor()
				mysqlCursor.execute('SELECT bug_id,bug_type,reporter,bug_status,function_id,target_milestone,short_desc,cf_comment_cea,assigned_to,resolution,component_id,priority,cf_ipr,deadline  FROM bugs WHERE bug_id=%d'% bugid)
				resList = mysqlCursor.fetchone()
				if not resList:
					continue
				name = ''
				if resList[10]:
					name = self.getCompNameFromUid(resList[10],mysqlConn)
				if self.getApkBugsFromcode(self.appname,resList[6],name):
					if (resList[3] == 'VERIFIED_SW' and resList[9] in ['Validated', "Can't test"]) or resList[3] == 'DELIVERED':
						if self.appname not in self.prVeriSWFromCodeInfoDict.keys():
							self.prVeriSWFromCodeInfoDict[self.appname] = {}
						self.prVeriSWFromCodeInfoDict[self.appname][bugid] = {}
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['type'] = resList[1]
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['reporter'] = self.getUserNameFromUid(resList[2], mysqlConn)
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['status'] = resList[3]
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['ownerinfo'] = self.getOwnerInfo(bugid, lastVerTimeStr, curVerTimeStr, mysqlConn, resList[8])
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['function'] = self.getFunctionName(resList[4], mysqlConn)
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['milestone'] = resList[5]
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['desc'] = resList[6]
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['commentcea'] = resList[7]
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['priority'] = resList[9]
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['ipr'] = resList[10]
						if not resList[11]:
							self.prVeriSWFromCodeInfoDict[self.appname][bugid]['deadline'] = ''
						else:
							self.prVeriSWFromCodeInfoDict[self.appname][bugid]['deadline'] = resList[11]
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['localpath'] = self.prFromCodeDict[self.appname][bugid]['localPath']
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['impact'] = self.prFromCodeDict[self.appname][bugid]['moduleImpact'].decode('utf8')
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['suggestion'] = self.prFromCodeDict[self.appname][bugid]['testSuggestion'].decode('utf8')
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['persoregen'] = 'Unknown'
						if resList[3] == 'VERIFIED_SW':
							self.needDeliverPR = True
					if resList[3] == 'RESOLVED':
						if self.appname not in self.prResolveFromCodeInfoDict.keys():
							self.prResolveFromCodeInfoDict[self.appname] = {}
						self.prResolveFromCodeInfoDict[self.appname][bugid] = {}
						self.prResolveFromCodeInfoDict[self.appname][bugid]['type'] = resList[1]
						self.prResolveFromCodeInfoDict[self.appname][bugid]['reporter'] = self.getUserNameFromUid(resList[2], mysqlConn)
						self.prResolveFromCodeInfoDict[self.appname][bugid]['status'] = resList[3]
						self.prResolveFromCodeInfoDict[self.appname][bugid]['ownerinfo'] = self.getOwnerInfo(bugid, lastVerTimeStr, curVerTimeStr, mysqlConn, resList[8])
						self.prResolveFromCodeInfoDict[self.appname][bugid]['function'] = self.getFunctionName(resList[4], mysqlConn)
						if resList[5]:
							self.prResolveFromCodeInfoDict[self.appname][bugid]['milestone'] = resList[5]
						else:
							self.prResolveFromCodeInfoDict[self.appname][bugid]['milestone'] = 'N/A'
						self.prResolveFromCodeInfoDict[self.appname][bugid]['desc'] = resList[6]
						self.prResolveFromCodeInfoDict[self.appname][bugid]['commentcea'] = resList[7]
						self.prResolveFromCodeInfoDict[self.appname][bugid]['priority'] = resList[9]
						self.prResolveFromCodeInfoDict[self.appname][bugid]['ipr'] = resList[10]
						if not resList[11]:
							self.prResolveFromCodeInfoDict[self.appname][bugid]['deadline'] = ''
						else:
							self.prResolveFromCodeInfoDict[self.appname][bugid]['deadline'] = resList[11]
						self.prResolveFromCodeInfoDict[self.appname][bugid]['localpath'] = self.prFromCodeDict[self.appname][bugid]['localPath']
						self.prResolveFromCodeInfoDict[self.appname][bugid]['impact'] = self.prFromCodeDict[self.appname][bugid]['moduleImpact'].decode('utf8')
						self.prResolveFromCodeInfoDict[self.appname][bugid]['suggestion'] = self.prFromCodeDict[self.appname][bugid]['testSuggestion'].decode('utf8')
						self.prResolveFromCodeInfoDict[self.appname][bugid]['persoregen'] = 'Unknown'
			mysqlCursor.close()


	def getCloneProjectBugID(self, bugid, appname):	
		self.getBrotherBugs(bugid, appname)
		self.getCloneFromBugs(bugid, appname)
		self.getParentBugs(bugid, appname)

	def getCloneProjectBugInfo(self,conf,bugid,clone_id,curVerTimeStr,lastVerTimeStr,appname):				
		mysqlConn = MySQLdb.connect('172.24.61.199', port=3306, user='scm_tools', passwd='SCM_TOOLS123!', db='bugs', charset='gbk')
		mysqlCursor = mysqlConn.cursor()
		mysqlCursor.execute('SELECT bug_id,product_id,bug_type,reporter,bug_status,function_id,target_milestone,short_desc,assigned_to,resolution,priority,cf_ipr,deadline FROM bugs WHERE bug_id=%d'% clone_id)
		resList = mysqlCursor.fetchone()
		productID = resList[1]
		mysqlCursor.execute('SELECT name FROM products WHERE id="%d"' % int(productID))
		productIdNumStr = str(mysqlCursor.fetchone()[0])

		if resList and productIdNumStr != self.AlmCheckDict[appname]['apkproject']:
			print "The bug's brother is %s" % resList[0]
			if bugid not in self.brotherBugsDict.keys():			
				self.brotherBugsDict[bugid] = []
			brotherBugsDict = {}							
			brotherBugsDict['GenericApp_BugID'] = bugid
			brotherBugsDict['Project_BugID'] = resList[0]
			brotherBugsDict['Product_name'] = productIdNumStr
			brotherBugsDict['type'] = resList[2]
			brotherBugsDict['reporter'] = self.getUserNameFromUid(resList[3], mysqlConn)
			brotherBugsDict['status'] = resList[4]
			brotherBugsDict['ownerinfo'] = self.getOwnerInfo(clone_id, lastVerTimeStr, curVerTimeStr, mysqlConn, resList[8])
			brotherBugsDict['function'] = self.getFunctionName(resList[5], mysqlConn)
			brotherBugsDict['milestone'] = resList[6]
			brotherBugsDict['desc'] = resList[7]
			brotherBugsDict['priority'] = resList[10]
			brotherBugsDict['ipr'] = resList[11]
			if not resList[12]:
				brotherBugsDict['deadline'] = ''
			else:
				brotherBugsDict['deadline'] = resList[12]
			self.brotherBugsDict[bugid].append(brotherBugsDict)
	def getBrotherBugs(self, bugID, appname):
		mysqlConn = MySQLdb.connect('172.24.61.199', port=3306, user='scm_tools', passwd='SCM_TOOLS123!', db='bugs', charset='gbk')
		mysqlCursor = mysqlConn.cursor()	
		mysqlCursor.execute('SELECT brother_ from brothers where brother=%d'% bugID)
		resList = mysqlCursor.fetchall()
		if resList:
			for bug in resList:
				mysqlCursor = mysqlConn.cursor()
				mysqlCursor.execute('SELECT product_id FROM bugs WHERE bug_id=%d'% bug)
				product_name_id = mysqlCursor.fetchone()[0]			
				mysqlCursor.execute('SELECT name FROM products WHERE id="%d"' % int(product_name_id))
				productname = mysqlCursor.fetchone()[0]
				if bug[0] not in self.bygForCirle:
					self.bygForCirle.append(bug[0])
				if productname != self.AlmCheckDict[appname]['apkproject']:
					if bug[0] not in self.cloneBugs:
						self.cloneBugs.append(bug[0])	



	def getParentBugs(self, bugID, appname):
		mysqlConn = MySQLdb.connect('172.24.61.199', port=3306, user='scm_tools', passwd='SCM_TOOLS123!', db='bugs', charset='gbk')
		mysqlCursor = mysqlConn.cursor()
		mysqlCursor.execute('SELECT blocked from dependencies where dependson=%d'% bugID)
		resList = mysqlCursor.fetchall()
		if resList:
			for bug in resList:
				mysqlCursor.execute('SELECT product_id FROM bugs WHERE bug_id=%d'% bug[0])
				product_name_id = mysqlCursor.fetchone()[0]			
				mysqlCursor.execute('SELECT name FROM products WHERE id="%d"' % int(product_name_id))
				productname = mysqlCursor.fetchone()[0]
				if bug[0] not in self.bygForCirle:
					self.bygForCirle.append(bug[0])
				if productname != self.AlmCheckDict[appname]['apkproject']:
					if bug[0] not in self.cloneBugs: 
						self.cloneBugs.append(bug[0])		


	def getCloneFromBugs(self, bugID, appname):		
		mysqlConn = MySQLdb.connect('172.24.61.199', port=3306, user='scm_tools', passwd='SCM_TOOLS123!', db='bugs', charset='gbk')
		mysqlCursor = mysqlConn.cursor()
		mysqlCursor.execute('SELECT bug_id from bugs where cf_colonefrom=%d'% bugID)
		resList = mysqlCursor.fetchall()				
		if resList:
			for bug in resList:
				mysqlCursor.execute('SELECT product_id FROM bugs WHERE bug_id=%d'% bug[0])
				product_name_id = mysqlCursor.fetchone()[0]			
				mysqlCursor.execute('SELECT name FROM products WHERE id="%d"' % int(product_name_id))
				productname = mysqlCursor.fetchone()[0]
				if bug[0] not in self.bygForCirle:
					self.bygForCirle.append(bug[0])
				if productname != self.AlmCheckDict[appname]['apkproject']:
					if bug[0] not in self.cloneBugs:
						self.cloneBugs.append(bug[0])			
	def getBugInforFromCodeButNotOfGenericapp(self, bugid, key, prNotGenericApkFromCodeDict):
		mysqlConn = MySQLdb.connect('172.24.61.199', port=3306, user='scm_tools', passwd='SCM_TOOLS123!', db='bugs', charset='gbk')		
		mysqlCursor = mysqlConn.cursor()
		mysqlCursor.execute('SELECT bug_id,product_id,bug_type,reporter,bug_status,function_id,target_milestone,short_desc,assigned_to,resolution,priority,cf_ipr,deadline FROM bugs WHERE bug_id=%d'% bugid)
		resList = mysqlCursor.fetchone()
		if resList:		
			productID = resList[1]
			mysqlCursor.execute('SELECT name FROM products WHERE id="%d"' % int(productID))
			productIdNumStr = str(mysqlCursor.fetchone()[0])
		oneProductIdNum = self.AlmCheckDict[key]['apkproject']
		if resList and productIdNumStr != oneProductIdNum:						
			prNotGenericApkFromCodeDict[bugid]['BugID'] = resList[0]
			prNotGenericApkFromCodeDict[bugid]['Product_name'] = productIdNumStr
			prNotGenericApkFromCodeDict[bugid]['type'] = resList[2]
			prNotGenericApkFromCodeDict[bugid]['reporter'] = self.getUserNameFromUid(resList[3], mysqlConn)
			prNotGenericApkFromCodeDict[bugid]['status'] = resList[4]
			prNotGenericApkFromCodeDict[bugid]['ownerinfo'] = self.getUserNameFromUid(resList[8], mysqlConn)
			prNotGenericApkFromCodeDict[bugid]['function'] = self.getFunctionName(resList[5], mysqlConn)
			prNotGenericApkFromCodeDict[bugid]['milestone'] = resList[6]
			prNotGenericApkFromCodeDict[bugid]['desc'] = resList[7]	
			prNotGenericApkFromCodeDict[bugid]['priority'] = resList[10]
			prNotGenericApkFromCodeDict[bugid]['ipr'] = resList[11]
			if not resList[12]:
				prNotGenericApkFromCodeDict[bugid]['deadline'] = ''
			else:
				prNotGenericApkFromCodeDict[bugid]['deadline'] = resList[12]

	def getApkBugsFromcode(self, apkname, dec,component):
		descriptionlist = dec.strip().split(' ')
		dec = ''.join(descriptionlist)
		componentList = component.strip().split(' ')
		component = ''.join(componentList)
		if re.search('\[\s*'+ apkname,dec,re.I) or re.search('\[\s*'+ apkname,dec,re.I) or re.search(apkname,component,re.I) or re.search(apkname,component,re.I):
			return True
		else:
			return False

	def getProductName(self,bugid):
		mysqlConn = MySQLdb.connect('172.24.61.199', port=3306, user='scm_tools', passwd='SCM_TOOLS123!', db='bugs', charset='gbk')		
		mysqlCursor = mysqlConn.cursor()
		mysqlCursor.execute('SELECT bug_id,product_id FROM bugs WHERE bug_id=%d'% bugid)
		resList = mysqlCursor.fetchone()
		if resList:		
			productID = resList[1]
			mysqlCursor.execute('SELECT name FROM products WHERE id="%d"' % int(productID))			
			productIdNumStr = str(mysqlCursor.fetchone()[0])
			return productIdNumStr
		else:
			productIdNumStr = ''
			return productIdNumStr






			
