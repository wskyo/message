#!/usr/bin/python
#coding=utf-8
############################################################################
## DB Utils for connection datebase and update PR status from browser.
## add by jianbo.deng for superspam create 2013-08-28
############################################################################
import MySQLdb
from time import strftime, localtime
from Integrity import IntegrityClient
import datetime
import time
import mechanize
import re
import sys
import os
from Utils import *
from Config import *
from UserInfo import *
import common

class DBUtilsALM:
	needDeliverPR = False
	almlogname = 'hz.int'		
	almpaword = 'ptc'
	isLogedInBugzilla = False
        url = "https://alm.tclcom.com:7003/webservices/10/2/Integrity/?wsdl"
	def __init__(self):
		self.login = ""
		##self.db_conn
		self.get_db_connection()	

	def get_db_connection(self):
		try:
            		common.show("%s Connect to alm" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
			self.db_conn = IntegrityClient(self.url, credential_username='hz.int', credential_password='ptc')
			common.show("Connect to alm OK")
			return self.db_conn
		except Exception, e:
			print e
			sys.exit(1)

	def get_db_connection_for_delivered(self,almloginname,almpassword):
		try:
            		common.show("%s Connect to alm" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
			self.db_conn = IntegrityClient(self.url, credential_username = almloginname, credential_password = almpassword)
			print "Login ALM ok"
			self.login = "sucess"
			return self.db_conn
		except Exception, e:
			print e
			print "Login ALM fail, try again..."
			self.login = "fail"


	## get VERIFIED_SW and RESOLVED PR 
	def getSWAndRelPRListFromAlm(self, conf, curVerTimeStr, lastVerTimeStr, AlmCheckDict):
		if 'branch' in self.AlmCheckDict[self.appname].keys():
			bugBranch = self.AlmCheckDict[self.appname]['branch']
			branchArr = bugBranch.replace(',',"','")		
		if self.appname in self.prFromCodeDict.keys():		
			for bugid in self.prFromCodeDict[self.appname].keys():						
				resList = self.db_conn.getItemsByCustomQuery(fields=['ID','Type','Created By','State','Function','New Ref','Summary','All CEA comments','Assigned User','Resolution','SW Release','Reporter Department','singleBranch','Deadline','IPR Value','Priority'], query="(field[ID] = %s)" % bugid)
				if not resList:
					continue			#except:	
				if (resList[0].branch in branchArr):
			#end add for sw release 2015-3-12
					if (resList[0].state == 'Verified_SW' and resList[0].resolution in ['Validated', "Can't test", "Monitor"]) or resList[0].state == 'Delivered':
						if self.appname not in self.prVeriSWFromCodeInfoDict.keys():
							self.prVeriSWFromCodeInfoDict[self.appname] = {}
						self.prVeriSWFromCodeInfoDict[self.appname][bugid] = {}
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['type'] = resList[0].type
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['reporter'] = self.creat_email(resList[0])
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['status'] = resList[0].state
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['ownerinfo'] = self.assigned_email(resList[0])
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['function'] = resList[0].function
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['milestone'] = resList[0].new_ref
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['desc'] = resList[0].summary
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['commentcea'] = resList[0].all_cea_comments
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['priority'] = resList[0].priority
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['ipr'] = resList[0].ipr_value
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['deadline'] = resList[0].deadline
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['localpath'] = self.prFromCodeDict[self.appname][bugid]['localPath']

						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['impact'] = self.prFromCodeDict[self.appname][bugid]['moduleImpact'].decode('utf8')
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['suggestion'] = self.prFromCodeDict[self.appname][bugid]['testSuggestion'].decode('utf8')
						self.prVeriSWFromCodeInfoDict[self.appname][bugid]['persoregen'] = 'Unknown'
						if resList[0].state == 'Verified_SW' or resList[0].state == 'Delivered':
							self.needDeliverPR = True
					if resList[0].state == 'Resolved':
						if self.appname not in self.prResolveFromCodeInfoDict.keys():
							self.prResolveFromCodeInfoDict[self.appname] = {}
						self.prResolveFromCodeInfoDict[self.appname][bugid] = {}
						self.prResolveFromCodeInfoDict[self.appname][bugid]['type'] = resList[0].type
						self.prResolveFromCodeInfoDict[self.appname][bugid]['reporter'] = self.creat_email(resList[0])
						self.prResolveFromCodeInfoDict[self.appname][bugid]['status'] = resList[0].state
						self.prResolveFromCodeInfoDict[self.appname][bugid]['ownerinfo'] = self.assigned_email(resList[0])
						self.prResolveFromCodeInfoDict[self.appname][bugid]['function'] = resList[0].function
						if resList[0].new_ref:
							self.prResolveFromCodeInfoDict[self.appname][bugid]['milestone'] = resList[0].new_ref
						else:
							self.prResolveFromCodeInfoDict[self.appname][bugid]['milestone'] = 'N/A'
						self.prResolveFromCodeInfoDict[self.appname][bugid]['desc'] = resList[0].summary
						self.prResolveFromCodeInfoDict[self.appname][bugid]['commentcea'] = resList[0].all_cea_comments
						self.prResolveFromCodeInfoDict[self.appname][bugid]['priority'] = resList[0].priority
						self.prResolveFromCodeInfoDict[self.appname][bugid]['ipr'] = resList[0].ipr_value
						self.prResolveFromCodeInfoDict[self.appname][bugid]['deadline'] = resList[0].deadline
						self.prResolveFromCodeInfoDict[self.appname][bugid]['localpath'] = self.prFromCodeDict[self.appname][bugid]['localPath']
						self.prResolveFromCodeInfoDict[self.appname][bugid]['impact'] = self.prFromCodeDict[self.appname][bugid]['moduleImpact'].decode('utf8')
						self.prResolveFromCodeInfoDict[self.appname][bugid]['suggestion'] = self.prFromCodeDict[self.appname][bugid]['testSuggestion'].decode('utf8')
						self.prResolveFromCodeInfoDict[self.appname][bugid]['persoregen'] = 'Unknown'

	def getBugInforFromCodeButNotOfGenericappALm(self, conf, bugid, key, prNotGenericApkFromCodeDict):
		resList = self.db_conn.getItemsByCustomQuery(fields=['ID','Type','Created By','State','Function','New Ref','Summary','All CEA comments','Assigned User','Resolution','In Project','New Ref','singleBranch','Deadline','IPR Value','Priority'], query="(field[ID] = %s)" % bugid)		
		if resList:
			curBugProductId = resList[0]['In Project']['IBPL'][0]
			resList1 = self.db_conn.getItemsByCustomQuery(fields=['Project'], query="(field[ID] = %d)" % curBugProductId)
			productIdNumStr = resList1[0]['Project'][1].value
			oneProductIdNumALM = self.AlmCheckDict[key]['apkproject']
			if productIdNumStr != oneProductIdNumALM:						
				prNotGenericApkFromCodeDict[bugid]['BugID'] = resList[0].id
				#self.prNotGenericApkFromCodeDict[key]['Project_BugID'] = resList[0]
				prNotGenericApkFromCodeDict[bugid]['Product_name'] = productIdNumStr
				prNotGenericApkFromCodeDict[bugid]['type'] = resList[0].type
				prNotGenericApkFromCodeDict[bugid]['reporter'] = resList[0].created_user.email
				prNotGenericApkFromCodeDict[bugid]['status'] = resList[0].state
				prNotGenericApkFromCodeDict[bugid]['ownerinfo'] = resList[0].assigned_user.email
				prNotGenericApkFromCodeDict[bugid]['function'] = resList[0].function
				prNotGenericApkFromCodeDict[bugid]['milestone'] = resList[0].new_ref
				prNotGenericApkFromCodeDict[bugid]['desc'] = resList[0].summary	
				prNotGenericApkFromCodeDict[bugid]['branch'] = resList[0].branch	
				prNotGenericApkFromCodeDict[bugid]['priority'] = resList[0].priority
				prNotGenericApkFromCodeDict[bugid]['ipr'] = resList[0].ipr_value
				prNotGenericApkFromCodeDict[bugid]['deadline'] = resList[0].deadline	



	def getVeriSWOldResolveInfoDictALM(self, oneProductIdNum, prVeriSWOldResolveInfoDict, prResolveFromBugzillaInfoDict,curVerTimeStr, lastVerTimeStr,AlmCheckDict):		
		if curVerTimeStr:
			State = "Verified_SW"
			Resolution1 = "Validated"
			Resolution2 = "Can\'t test"
			Resolution3 = "Monitor"						
			mysqlCursor = self.db_conn.getItemsByCustomQuery(fields=['ID','Type','Created By','State','Function','New Ref','Summary','All CEA comments','Assigned User','Resolution','SW Release','Reporter Department','singleBranch','Last Verified_SW Date','Deadline','IPR Value','Priority'], query="((field[State] = %s) and ((field[Resolution] = %s) or (field[Resolution] = %s) or (field[Resolution] = %s)) and (field[In Project] = %s))" % (State, Resolution1,Resolution2,Resolution3,oneProductIdNum))
			NumOfBugs = len(mysqlCursor)
			if NumOfBugs:				
				for i in mysqlCursor:
					bugid = i.ID.integer.value
					branchName = i.branch
					if bugid in self.prVeriSWFromCodeInfoDict.keys():
						continue
					if not self.checkManualChangePR(bugid, branchName):
						continue					
					if self.appname in self.prVeriSWFromCodeInfoDict.keys():
						if bugid in self.prVeriSWFromCodeInfoDict[self.appname].keys():
							continue			
					
					if self.compare_two_time(curVerTimeStr,i.last_time_to_set_sw):
					##begin add by laiyinfang 2014-04-16
						prResolveFromBugzillaInfoDict[bugid] = {}
						prResolveFromBugzillaInfoDict[bugid]['type'] = i.type
						prResolveFromBugzillaInfoDict[bugid]['reporter'] = self.creat_email(i)
						prResolveFromBugzillaInfoDict[bugid]['status'] = i.state
						prResolveFromBugzillaInfoDict[bugid]['ownerinfo'] = self.assigned_email(i)
						prResolveFromBugzillaInfoDict[bugid]['function'] = i.function
						prResolveFromBugzillaInfoDict[bugid]['milestone'] = i.new_ref
						prResolveFromBugzillaInfoDict[bugid]['desc'] = i.summary
						prResolveFromBugzillaInfoDict[bugid]['commentcea'] = i.all_cea_comments
						prResolveFromBugzillaInfoDict[bugid]['priority'] = i.priority
						prResolveFromBugzillaInfoDict[bugid]['ipr'] = i.ipr_value
						prResolveFromBugzillaInfoDict[bugid]['deadline'] = i.deadline
						prResolveFromBugzillaInfoDict[bugid]['localpath'] = ''
						prResolveFromBugzillaInfoDict[bugid]['impact'] =''
						prResolveFromBugzillaInfoDict[bugid]['suggestion'] = ''
						prResolveFromBugzillaInfoDict[bugid]['persoregen'] = 'Unknown'
						prResolveFromBugzillaInfoDict[bugid]['component'] = ''
						##end add by laiyinfang 2014-04-16
						continue
					prVeriSWOldResolveInfoDict[bugid] = {}
					prVeriSWOldResolveInfoDict[bugid]['type'] = i.type
					prVeriSWOldResolveInfoDict[bugid]['reporter'] = self.creat_email(i)
					prVeriSWOldResolveInfoDict[bugid]['status'] = i.state
					prVeriSWOldResolveInfoDict[bugid]['ownerinfo'] = self.assigned_email(i)
					prVeriSWOldResolveInfoDict[bugid]['function'] = i.function
					prVeriSWOldResolveInfoDict[bugid]['milestone'] = i.new_ref
					prVeriSWOldResolveInfoDict[bugid]['desc'] = i.summary
					prVeriSWOldResolveInfoDict[bugid]['commentcea'] = i.all_cea_comments
					prVeriSWOldResolveInfoDict[bugid]['priority'] = i.priority
					prVeriSWOldResolveInfoDict[bugid]['ipr'] = i.ipr_value
					prVeriSWOldResolveInfoDict[bugid]['deadline'] = i.deadline
					prVeriSWOldResolveInfoDict[bugid]['impact'] = ''
					prVeriSWOldResolveInfoDict[bugid]['suggestion'] = ''
					prVeriSWOldResolveInfoDict[bugid]['persoregen'] = 'Unknown'
					prVeriSWOldResolveInfoDict[bugid]['component'] = ''
					self.needDeliverPR = True

	def deliverPRlistALM(self, conf, mysqlConn, prVeriSWOldResolveInfoDict,prResolveFromBugzillaInfoDict):
		if self.needDeliverPR :
			appBugs={}			
			for bugid,buginfo in prVeriSWOldResolveInfoDict.items():				
				print "veri sw old resovle pr ------ %s" % bugid
				if buginfo['status'] in ['Verified_SW', 'Delivered']:
					if self.appname not in self.prNeedDelivHash.keys():
						self.prNeedDelivHash[self.appname] = {}
					self.prNeedDelivHash[self.appname][bugid] = [buginfo['status'], buginfo['milestone']]			
					appBugs[bugid] = buginfo
					appBugs[bugid]['status'] = 'Delivered'
			if self.appname in self.prVeriSWFromCodeInfoDict.keys():
				for bugid,buginfo in self.prVeriSWFromCodeInfoDict[self.appname].items():				
					print "veri sw resovle pr ------ %s" % bugid
					if buginfo['status'] in ['Verified_SW', 'Delivered']:
						if self.appname not in self.prNeedDelivHash.keys():
							self.prNeedDelivHash[self.appname] = {}
						self.prNeedDelivHash[self.appname][bugid] = [buginfo['status'], buginfo['milestone']]	
						appBugs[bugid] = buginfo
						appBugs[bugid]['status'] = 'Delivered'
			if appBugs:	
				self.apkDeliveredBugs[self.appname] = appBugs.copy()
			appBugs = {}


			

		noNeedDeliveredBugs = {}
		for bugid,buginfo in prResolveFromBugzillaInfoDict.items():			
			print "veri sw old resovle from buzilla no need delivered pr ------ %s" % bugid, buginfo['milestone']				
			noNeedDeliveredBugs[bugid] = buginfo
		if self.appname in self.prResolveFromCodeInfoDict.keys():
			for bugid,buginfo in self.prResolveFromCodeInfoDict[self.appname].items():				
				print "veri sw old resovle from code  no need delivered pr ------ %s" % bugid, buginfo['milestone']
				noNeedDeliveredBugs[bugid] = buginfo
		if noNeedDeliveredBugs:	
			self.apkSWNoDeliveredBugs[self.appname] = noNeedDeliveredBugs.copy()
		noNeedDeliveredBugs = {}
			
	 


	def creat_email(self, anobj):
		if not anobj.created_user:
			email_address = ''
		else:
			email_address = anobj.created_user.email
		return email_address


	def assigned_email(self, anobj):
		if not anobj.assigned_user:
			email_address = ''
		else:
			email_address = anobj.assigned_user.email
		return email_address

	def checkManualChangePR(self, bugid, branchName):
		if 'branch' in self.AlmCheckDict[self.appname].keys():
			bugBranch = self.AlmCheckDict[self.appname]['branch']
			branchArr = bugBranch.replace(',',"','")
			if branchName in branchArr:
				print "bug id------------------> %d"%bugid
				return True
			else :
				print "bug id------------------> %d"%bugid
				print "not right branch------------------> %s"%branchName
				return False
		else:
			print "The %s app has no branch in alm" % self.appname
			return False

	def getPrFromCodeListForOneApkALM(self, conf, bugid, appname):
		oneProductIdNumALM = ''
		print "the bugid is %s" % bugid	
		oneProductIdNumALM = self.AlmCheckDict[appname]['apkproject']
		print "the prject name of conf is %s" % oneProductIdNumALM
		resList = self.db_conn.getItemsByCustomQuery(fields=['ID','In project'], query="(field[ID] = %s)" % bugid)
		if not resList:
			curBugProductId =''
			curBugProductName = ''	
		if resList[0]:		
			curBugProductId = resList[0]['In Project']['IBPL'][0]			
			resList1 = self.db_conn.getItemsByCustomQuery(fields=['Project'], query="(field[ID] = %d)" % curBugProductId)
			if resList1[0]:
				curBugProductName = resList1[0]['Project'][1].value
				print "the bug's project name is %s" % curBugProductName
		else:
			curBugProductId =''
			curBugProductName = ''			
				
		if curBugProductName == oneProductIdNumALM:				
				return True
		else:
				return False


	def compare_two_time(self,start_t,end_t):
		s_time = time.mktime(time.strptime(start_t,'%Y-%m-%d %H:%M:%S')) # get the seconds for specify date
		e_time = time.mktime(time.strptime(end_t,'%Y-%m-%d %H:%M:%S'))		
		if (float(s_time) < float(e_time)):
			return True
		return False



	### deliver PR status from browser user mechanize
	def deliverPRALM(self, conf, prHash,version):
		print "Now start to delivered verified_sw bugs"
		countPRNeedDeliver = 0
		curPRDeliverNumber = 1		
		#Login = " "
		for pr,infoList in prHash.items():
			if not infoList:
				continue
			if infoList[0] in ['Verified_SW', 'Delivered']:
				countPRNeedDeliver += 1
		print 'CAUTION: %d PRs are to be delivered or be added comment' % countPRNeedDeliver
		for pr,infoList in prHash.items():
			if infoList[0] in ['Verified_SW', 'Delivered']:
				if not self.isLogedInBugzilla:
					while True:
						if not self.almlogname and not self.almpaword:				
							self.almlogname = conf.getConf('almloginname', 'ALM loggin name', ask=2)
							self.almpaword = conf.getConf('almpassword', 'ALM password', ask=2, echo=False)
						self.get_db_connection_for_delivered(self.almlogname, self.almpaword)			
						print "The value of login is %s" % self.login
						if re.match('^sucess$',self.login):
							print "Login ALM ok"
							break	
						elif re.match('^fail$',self.login):
							print "Login ALM fail, try again..."
					self.isLogedInBugzilla = True
				try:
					#version = conf.getConf('version','current version')
					verstr = 'v%s' % version
					fullName = conf.getConf('almloginname', 'almloginname', 'hudson.admin')
					comment = 'The new ref is updated by %s with int tool superspam\n' % fullName
					if infoList[0] == 'Verified_SW':
						comment += 'Change bug status to DELIVERED\n'						
					comment += 'New ref: %s' % verstr
					comment += '\nPlease use %s to verify' % verstr	
					if infoList[0] == 'Verified_SW':
						new_ref = infoList[1]
					if not re.search('\s%s\s' % verstr, new_ref) and not re.search('\s%s$' % verstr, new_ref):
						new_ref = verstr
					print "The bugid is %s" % pr
					print "The new ref is %s" % new_ref
					print "The comment is %s" % comment
					#self.db_conn.editItem(item_id = "%s", **{'New Ref':"%s",'Additional Comments':"%s",'State':'Delivered'} % (pr,new_ref,comment))			
					self.db_conn.editItem(item_id = pr, **{'New Ref':new_ref,'Additional Comments':comment,'State':'Delivered'})
				except Exception, e:
					print e
					print 'WARNING: Deliver PR %s fail, please check' % str(pr)
					
			else:
				pass	

	def create_releasenote(self, conf, version):
		project = self.AlmCheckDict[self.appname]['apkproject']
		branch = self.AlmCheckDict[self.appname]['branch']		
		state = "Active"
		version = 'v%s' % version		
		if self.almlogname:		
			print "You have logined ALM"
		else:
			self.almlogname = conf.getConf('almloginname', 'ALM loggin name', ask=2)
			self.almpaword = conf.getConf('almpassword', 'ALM password', ask=2, echo=False)
			print "You logined in ALM just now"			
		self.db_conn = IntegrityClient(self.url, credential_username=self.almlogname, credential_password=self.almpaword)
		self.db_conn.createReleaseNote(State=state,InProject=project,Branch=branch,Version=version)
		match = re.search('\/.*\/(.*)\/', project)
		project_gapp = project
		project_gapp = project_gapp.replace(match.group(1),"Others")
		project_gapp = project_gapp + " for GAPP"
		print "The gapp projetc name is %s" % project_gapp
		projects = self.getproject()
		for item in projects:
			if item.Name == project_gapp:
				print "The Gapp name of projetc is existing"
				self.db_conn.createReleaseNote(State=state,InProject=project_gapp, Branch=branch,Version=version)	


	def getproject(self):		
		self.get_db_connection()
		projects = self.db_conn.getProjects(fields=['Description', 'Name','ID'])
		return projects	
	
	def getCloneProjectBugIDALM(self, bugid, appname):	
		self.getBrotherBugsALM(bugid, appname,self.cloneBugs)

	def getBrotherBugsALM(self, bugID, appname, cloneBugs):
		resList = self.db_conn.getItemsByCustomQuery(fields=['ID','Type','Parent item','Child Items', 'Brother Items', 'In Project'], query="(field[ID] = %s)" % bugID)
		project = self.AlmCheckDict[appname]['apkproject']
		if resList:
			for item in resList:
				if 'Parent item' in item.keys():
					for defect in item['Parent item'][1]:			
						result = self.db_conn.getItemsByCustomQuery(fields=['ID','In Project'], query="(field[ID] = %s)" % defect)
						curBugProductId = result[0]['In Project']['IBPL'][0]
						resList1 = self.db_conn.getItemsByCustomQuery(fields=['Project'], query="(field[ID] = %d)" % curBugProductId)
						productname = resList1[0]['Project'][1].value
						if productname != project:
							if defect not in cloneBugs:
								cloneBugs.append(defect)
				if 'Child Items' in item.keys():			
					for defect in item['Child Items'][1]:			
						result = self.db_conn.getItemsByCustomQuery(fields=['ID','In Project'], query="(field[ID] = %s)" % defect)
						curBugProductId = result[0]['In Project']['IBPL'][0]
						resList1 = self.db_conn.getItemsByCustomQuery(fields=['Project'], query="(field[ID] = %d)" % curBugProductId)
						productname = resList1[0]['Project'][1].value
						if productname != project:
							if defect not in cloneBugs:
								cloneBugs.append(defect)

				if 'Brother Items' in item.keys():			
					for defect in item['Brother Items'][1]:			
						result = self.db_conn.getItemsByCustomQuery(fields=['ID','In Project'], query="(field[ID] = %s)" % defect)
						curBugProductId = result[0]['In Project']['IBPL'][0]
						resList1 = self.db_conn.getItemsByCustomQuery(fields=['Project'], query="(field[ID] = %d)" % curBugProductId)
						productname = resList1[0]['Project'][1].value
						if productname != project:
							if defect not in cloneBugs:
								cloneBugs.append(defect)


	def getCloneProjectBugInfoALM(self,conf,bugid,clone_id,curVerTimeStr,lastVerTimeStr,appname):
		project = self.AlmCheckDict[appname]['apkproject']				
		resList = self.db_conn.getItemsByCustomQuery(fields=['ID','Type','Created By','State','Function','New Ref','Summary','All CEA comments','Assigned User','Resolution','SW Release','Reporter Department','singleBranch','In Project','Deadline','IPR Value','Priority'], query="(field[ID] = %s)" % clone_id)	
		for item in resList:
			if not item:
				continue
			curBugProductId = item['In Project']['IBPL'][0]
			resList1 = self.db_conn.getItemsByCustomQuery(fields=['Project'], query="(field[ID] = %d)" % curBugProductId)
			productIdNumStr = resList1[0]['Project'][1].value			  
			if productIdNumStr != project:
				if bugid not in self.brotherBugsDict.keys():			
					self.brotherBugsDict[bugid] = []
				brotherBugsDict = {}							
				brotherBugsDict['GenericApp_BugID'] = bugid
				brotherBugsDict['Project_BugID'] = clone_id
				brotherBugsDict['Product_name'] = productIdNumStr
				brotherBugsDict['type'] = item.type
				brotherBugsDict['reporter'] = self.creat_email(item)
				brotherBugsDict['status'] = item.state
				brotherBugsDict['ownerinfo'] = self.assigned_email(item)
				brotherBugsDict['function'] = item.function
				brotherBugsDict['milestone'] = item.new_ref
				brotherBugsDict['desc'] = item.summary
				brotherBugsDict['branch'] = item.branch
				brotherBugsDict['priority'] = item.priority
				brotherBugsDict['ipr'] = item.ipr_value
				brotherBugsDict['deadline'] = item.deadline
				self.brotherBugsDict[bugid].append(brotherBugsDict)

	def createAssignment(self, conf, assginDict):		
		if self.almlogname:		
			print "You have logined ALM"
		else:
			self.almlogname = conf.getConf('almloginname', 'ALM loggin name', ask=2)
			self.almpaword = conf.getConf('almpassword', 'ALM password', ask=2, echo=False)
			print "You logined in ALM just now"			
		self.db_conn = IntegrityClient(self.url, credential_username=self.almlogname, credential_password=self.almpaword)
		assignID = self.db_conn.createAssignment(**assginDict)
		return assignID

	def EditCommentForDefect(self, conf, editDefectList, project, assignmentID):
		if self.almlogname:		
			print "You have logined ALM"
		else:
			self.almlogname = conf.getConf('almloginname', 'ALM loggin name', ask=2)
			self.almpaword = conf.getConf('almpassword', 'ALM password', ask=2, echo=False)
			print "You logined in ALM just now"
		self.get_db_connection_for_delivered(self.almlogname,self.almpaword)
		for defect in editDefectList:
			try:
				fullName = conf.getConf('almloginname', 'almloginname', 'hudson.admin')
				#comment = 'The comment is added by %s with int tool superspam\n' % fullName
				comment = 'The assignment %s has been created. When it has been qualified, the apk will been upload to %s code.' %(assignmentID, project)
				print "The bugid is %s" % defect
				print "The comment is %s" % comment		
				self.db_conn.editItem(item_id = defect, **{'Additional Comments':comment})
			except Exception, e:
				print e
				print 'WARNING: Edit Defect %s fail, please check' % str(defect)				
					
	def diffDefect(self, project, defectDict, defectList, branch):
		noCloneDect = []
		otherDefectNoPatched = []
		allNeedAddCommentList = []
		for item in defectDict:
			defectID = int(item.keys()[0])
			if defectID in defectList:
				continue
			resList = self.db_conn.getItemsByCustomQuery(fields=['ID','In Project','singleBranch'], query="(field[ID] = %s)" % item.keys()[0])
			if not resList:
				continue
			if resList[0]:
				curBugProductId = resList[0]['In Project']['IBPL'][0]		
				defectBranch = resList[0].branch				
				resList1 = self.db_conn.getItemsByCustomQuery(fields=['Project'], query="(field[ID] = %d)" % curBugProductId)
				if resList1[0]:
					productname = resList1[0]['Project'][1].value
			else:
				curBugProductId = ''
				defectBranch = ''
				productname = ''
			if productname == project and defectBranch in branch:
				noCloneDect.append(item.keys()[0])
			else:
				otherDefectNoPatched.append(item.keys()[0]) 	
		allNeedAddCommentList = noCloneDect + defectList
		return allNeedAddCommentList,otherDefectNoPatched	

			
	def getEdit_ResolvedAPKDefectForProjectBeforeHome(self, commentDefectList, appname, version, project, branch):
		if self.almlogname:		
			print "You have logined ALM"
		else:
			self.almlogname = conf.getConf('almloginname', 'ALM loggin name', ask=2)
			self.almpaword = conf.getConf('almpassword', 'ALM password', ask=2, echo=False)
			print "You logined in ALM just now"
		self.get_db_connection_for_delivered(self.almlogname,self.almpaword)
		for defect in commentDefectList:
			resList = self.db_conn.getItemsByCustomQuery(fields=['ID','State'], query="(field[ID] = %s)" % defect)
			if resList:
				if resList[0].state != 'Resolved':
					continue

			try:
				comment = '%s APK version %s has been pushed to %s branch %s code' % (appname, version, project, branch)		
				self.db_conn.editItem(item_id = defect, **{'Additional Comments':comment,'State':'Verified_SW','resolution':"Can't test"})
			except Exception, e:
				print e
				print 'WARNING: Edit Defect %s fail, please check' % str(defect)
	def getOnGoingDefectTask_of_Gapp(self, appname, onGoingDefectTaskDict):
		project = self.AlmCheckDict[appname]['apkproject']
		branch = self.AlmCheckDict[appname]['branch']
		if project and branch:
			mysqlCursor = self.db_conn.getItemsByCustomQuery(fields=['ID','Type','Created By','State','Summary','Assigned User','Resolution','SW Release','Deadline','IPR Value','Priority'], query="((field[Type]=Defect,task) and (field[State]=New,Assigned,Opened,Resolved) and (field[In Project] = %s) and (field[singleBranch] = %s))" % (project, branch))
			NumOfBugs = len(mysqlCursor)
			if NumOfBugs:				
				for i in mysqlCursor:
					bugid = i.ID.integer.value				
					if bugid in onGoingDefectTaskDict.keys():
						continue
					bugid = i.ID.integer.value
					onGoingDefectTaskDict[bugid] = {}
					onGoingDefectTaskDict[bugid]['type'] = i.type
					onGoingDefectTaskDict[bugid]['reporter'] = self.creat_email(i)
					onGoingDefectTaskDict[bugid]['status'] = i.state
					onGoingDefectTaskDict[bugid]['ownerinfo'] = self.assigned_email(i)
					onGoingDefectTaskDict[bugid]['desc'] = i.summary
					onGoingDefectTaskDict[bugid]['priority'] = i.priority
					onGoingDefectTaskDict[bugid]['ipr'] = i.ipr_value
					onGoingDefectTaskDict[bugid]['deadline'] = i.deadline


	def getDefectTypeStatus(self, bugid):
		projects = self.getproject()
		bugType = ''
		bugState = ''
		productname = ''
		items = self.db_conn.getItemsByCustomQuery(fields=['ID','Type','State','In project'], query="((field[ID]=%s))" % bugid )
		if not items:
			return bugType,bugState,productname
		else:       
			bugType = items[0]['Type'].type
			bugState = items[0]['State'].state
			curBugProductId = items[0]['In Project']['IBPL'][0]
		resList1 = self.db_conn.getItemsByCustomQuery(fields=['Project'], query="(field[ID] = %d)" % curBugProductId)
		if resList1[0]:
			productname = resList1[0]['Project'][1].value		
                print "get bug's Type and state"
                print bugType,bugState,productname
		return bugType,bugState,productname

	def diffDefectAndTask(self, prList):
		for bug in prList:
			items = self.db_conn.getItemsByCustomQuery(fields=['ID','Type'], query="((field[ID]=%s))" % bug)
			if not items:
				continue
			if items[0].type == 'Task':
				prList.remove(bug)
		return prList
