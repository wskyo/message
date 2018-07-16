#!/usr/bin/python
#coding=utf-8
############################################################################
## DB Utils for connection datebase and update PR status from browser.
## add by jianbo.deng for superspam create 2013-08-28
############################################################################
#import MySQLdb
from time import strftime, localtime
from Integrity import IntegrityClient
import datetime
import time
import mechanize
import re
import sys
import os
import common
from Utils import *
from Config import *
from UserInfo import *
#sys.setdefaultencoding('utf-8')


class DBUtilsAlm:
	almlogname = ''		
	almpaword = ''
	needDeliverPR = ''
	#url = "http://172.24.147.72:7001/webservices/10/2/Integrity/?wsdl"
	url = "https://alm.tclcom.com:7003/webservices/10/2/Integrity/?wsdl"
	def __init__(self):
		self.login = ""
		self.get_db_connection()
                self.projects = self.getproject()

	def get_db_connection(self):
		try:
            		common.show("%s Connect to alm" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
			self.db_conn = IntegrityClient(self.url, credential_username='hz.int', credential_password='ptc')
			
			return self.db_conn
		except Exception, e:
			print e
			print "change to cts server to login in"
			self.get_db_connection_bak()
			sys.exit(1)


	def getproject(self):		
		self.get_db_connection()
		projects = self.db_conn.getProjects(fields=['Description', 'Name','ID'])
		return projects


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
			#self.get_db_connection_for_delivered_bak(almloginname,almpassword)
			#sys.exit(1)
  

	def getIDNumberAndCodeList(self, conf, productIdNumList, prFromCodeList):
		self.projects = self.getproject()		 
		print "Now start to get IDNumber and codelist"					
		for productIdStr in self.getBugzillaProduct(conf):
			if not re.match('\d+', productIdStr):
				for i in self.projects:
					if productIdStr == i.Name:
						productIdNumStr = i.ID
						print "---The alm id is %s---" % i.ID
						print "---The PRODUCT alm id is %s---" % productIdNumStr
						break
						
			else:
				productIdNumStr = productIdStr
				print "The product alm id is %s" % productIdNumStr
			productIdNumList.append(productIdNumStr)

			print "--------productIdNumList is %s----------" % productIdNumList

		for bugid in self.prFromCodeDict.keys():
			resList = self.db_conn.getItemsByCustomQuery(fields=['Project'],query="((field[ID]=%s))" % bugid)
			if not resList:				
				continue			
			print "The relist is %s" % resList[0]
			if not resList[0]:
				continue
			curBugProductName = resList[0].project
			for i in self.projects:
				if curBugProductName == i.Name:
					curBugProductId = i.ID			
			if not curBugProductId in productIdNumList:
				continue
			prFromCodeList.append(bugid)
		prFromCodeList.sort()

	## get VERIFIED_SW and RESOLVED PR 
	def getSWAndRelPRList(self, conf, prFromCodeList, prVeriSWFromCodeInfoDict, prResolveFromCodeInfoDict, curVerTimeStr, lastVerTimeStr):
		bugBranch = conf.getConf('projbugbranch', 'project bugbranch',' ')
		branchArr = bugBranch.replace(',',"','")
		#add for filter sw release 2015-3-12
		sw_release,sw_release2 = self.getSwRelease(conf)
		#end add for filter sw release
			
		for bugid in prFromCodeList:						
			resList = self.db_conn.getItemsByCustomQuery(fields=['ID','Type','Created By','State','Function','New Ref','Summary','All CEA comments','Assigned User','Resolution','SW Release','Reporter Department','singleBranch'], query="(field[ID] = %s)" % bugid)
			if not resList:
				continue
			#add for sw release 2015-3-12
			if 'SW Release' in resList[0].keys():
				releasenoteID = resList[0]['SW Release'].IBPL[0]
				release = self.db_conn.getItemsByCustomQuery(fields=['ID','Version'], query="(field[ID] = %s)" % releasenoteID)
				ALMswRelease = release[0]['Version'][1].value
				ALMswRelease = ALMswRelease.upper()
			else:
				ALMswRelease = ''
			if (resList[0].branch in branchArr) and (re.search(sw_release,ALMswRelease) or re.search(sw_release2,ALMswRelease) or self.SWRelease_mini_check(ALMswRelease) or (resList[0].type=="Task")):
			#end add for sw release 2015-3-12
				if (resList[0].state == 'Verified_SW' and resList[0].resolution in ['Validated', "Can't test", "Monitor"]) or resList[0].state == 'Delivered':
					prVeriSWFromCodeInfoDict[bugid] = {}
					prVeriSWFromCodeInfoDict[bugid]['type'] = resList[0].type
					prVeriSWFromCodeInfoDict[bugid]['reporter'] = self.creat_email(resList[0])
					prVeriSWFromCodeInfoDict[bugid]['status'] = resList[0].state
					prVeriSWFromCodeInfoDict[bugid]['ownerinfo'] =  self.assigned_email(resList[0])
					prVeriSWFromCodeInfoDict[bugid]['function'] = resList[0].function
					prVeriSWFromCodeInfoDict[bugid]['milestone'] = resList[0].new_ref
					prVeriSWFromCodeInfoDict[bugid]['desc'] = resList[0].summary
					prVeriSWFromCodeInfoDict[bugid]['commentcea'] = resList[0].all_cea_comments
					prVeriSWFromCodeInfoDict[bugid]['localpath'] = self.prFromCodeDict[bugid]['localPath']
					prVeriSWFromCodeInfoDict[bugid]['impact'] = self.prFromCodeDict[bugid]['moduleImpact'].decode('utf8')
					prVeriSWFromCodeInfoDict[bugid]['menutree_iamge'] = self.prFromCodeDict[bugid]['menutree_iamge'].decode('utf8')
					prVeriSWFromCodeInfoDict[bugid]['suggestion'] = self.prFromCodeDict[bugid]['testSuggestion'].decode('utf8')
                                        #add by zhaoshie 20150612
				        prVeriSWFromCodeInfoDict[bugid]['rootcause'] = self.prFromCodeDict[bugid]['rootcause'].decode('utf8')
				        prVeriSWFromCodeInfoDict[bugid]['rootcauseDetail'] = self.prFromCodeDict[bugid]['rootcauseDetail'].decode('utf8')
				        prVeriSWFromCodeInfoDict[bugid]['Solution'] = self.prFromCodeDict[bugid]['Solution'].decode('utf8')
					prVeriSWFromCodeInfoDict[bugid]['persoregen'] = 'Unknown'
					prVeriSWFromCodeInfoDict[bugid]['assign_department'] = resList[0].created_user.fullname

					if resList[0].state == 'Verified_SW':
						self.needDeliverPR = True
				if resList[0].state == 'Resolved':
					prResolveFromCodeInfoDict[bugid] = {}
					prResolveFromCodeInfoDict[bugid]['type'] = resList[0].type
					prResolveFromCodeInfoDict[bugid]['reporter'] = self.creat_email(resList[0])
					prResolveFromCodeInfoDict[bugid]['status'] = resList[0].state
					prResolveFromCodeInfoDict[bugid]['ownerinfo'] = self.assigned_email(resList[0])
					prResolveFromCodeInfoDict[bugid]['function'] = resList[0].function
					if resList[0].new_ref:
						prResolveFromCodeInfoDict[bugid]['milestone'] = resList[0].new_ref
					else:
						prResolveFromCodeInfoDict[bugid]['milestone'] = 'N/A'
					prResolveFromCodeInfoDict[bugid]['desc'] = resList[0].summary
					prResolveFromCodeInfoDict[bugid]['commentcea'] = resList[0].all_cea_comments
					prResolveFromCodeInfoDict[bugid]['localpath'] = self.prFromCodeDict[bugid]['localPath']
					prResolveFromCodeInfoDict[bugid]['impact'] = self.prFromCodeDict[bugid]['moduleImpact'].decode('utf8')
					prResolveFromCodeInfoDict[bugid]['menutree_iamge'] = self.prFromCodeDict[bugid]['menutree_iamge'].decode('utf8')
					prResolveFromCodeInfoDict[bugid]['suggestion'] = self.prFromCodeDict[bugid]['testSuggestion'].decode('utf8')
                                        #add by zhaoshie 20150612
				        prResolveFromCodeInfoDict[bugid]['rootcause'] = self.prFromCodeDict[bugid]['rootcause'].decode('utf8')
				        prResolveFromCodeInfoDict[bugid]['rootcauseDetail'] = self.prFromCodeDict[bugid]['rootcauseDetail'].decode('utf8')
				        prResolveFromCodeInfoDict[bugid]['Solution'] = self.prFromCodeDict[bugid]['Solution'].decode('utf8')
					prResolveFromCodeInfoDict[bugid]['persoregen'] = 'Unknown'
					prResolveFromCodeInfoDict[bugid]['assign_department'] = resList[0].created_user.fullname
			

	### get PR old Resolve info
	##  begin modify by laiyinfang 2014-04-16
	def getVeriSWOldResolveInfoDict(self, productIdNumList, prVeriSWOldResolveInfoDict, prVeriSWFromCodeInfoDict,prResolveFromCodeInfoDict,curVerTimeStr, lastVerTimeStr, conf):
		productIdSqlList = []
		#projects = self.getproject()
		#add for filter sw release 2015-3-12
		sw_release,sw_release2 = self.getSwRelease(conf)
		#end add for filter sw release
		for oneProductIdNum in productIdNumList:
			print "The oneProductIdNum is %s" % oneProductIdNum
			for i in self.projects:			
				if  i.ID == oneProductIdNum:
					print "-------The product id is %s" % i.ID			
					productIdNumStr = i.Name								
					productIdSqlList.append('%s' % productIdNumStr)
					print "-------The product name is %s" % productIdSqlList
					break			
		if curVerTimeStr:
			State = "Verified_SW"
			Resolution1 = "Validated"
			Resolution2 = "Can\'t test"
			Resolution3 = "Monitor"
			for i in productIdSqlList:			
				mysqlCursor = self.db_conn.getItemsByCustomQuery(fields=['ID','Type','Created By','State','Function','New Ref','Summary','All CEA comments','Assigned User','Resolution','SW Release','Reporter Department','singleBranch','Last Verified_SW Date'], query="((field[State] = %s) and ((field[Resolution] = %s) or (field[Resolution] = %s) or (field[Resolution] = %s)) and (field[In Project] = %s))" % (State, Resolution1,Resolution2,Resolution3,i))
				NumOfBugs = len(mysqlCursor)
				if not NumOfBugs:
					continue
				for i in mysqlCursor:
					bugid = i.ID.integer.value
					branchName = i.branch
					if bugid in prVeriSWFromCodeInfoDict.keys():
						continue
					if not self.checkManualChangePR(conf, bugid, branchName):
						continue
					#add for sw release 2015-3-1				

					if 'SW Release' in i.keys():
						releasenoteID = i['SW Release'].IBPL[0]
						release = self.db_conn.getItemsByCustomQuery(fields=['ID','Version'], query="(field[ID] = %s)" % releasenoteID)
						ALMswRelease = release[0]['Version'][1].value
					else:
						ALMswRelease = ''
					if not i.last_time_to_set_sw:
						continue
					if self.compare_two_time(curVerTimeStr,i.last_time_to_set_sw) and (re.search(sw_release,ALMswRelease) or re.search(sw_release2,ALMswRelease) or self.SWRelease_mini_check(ALMswRelease) or (i.type=="Task")):
						##begin add by laiyinfang 2014-04-16
						prResolveFromCodeInfoDict[bugid] = {}
						prResolveFromCodeInfoDict[bugid]['type'] = i.type
						prResolveFromCodeInfoDict[bugid]['reporter'] = self.creat_email(i)
						prResolveFromCodeInfoDict[bugid]['status'] = i.state
						prResolveFromCodeInfoDict[bugid]['ownerinfo'] = self.assigned_email(i)
						prResolveFromCodeInfoDict[bugid]['function'] = i.function
						prResolveFromCodeInfoDict[bugid]['milestone'] = i.new_ref
						prResolveFromCodeInfoDict[bugid]['desc'] = i.summary
						prResolveFromCodeInfoDict[bugid]['commentcea'] = i.all_cea_comments
						prResolveFromCodeInfoDict[bugid]['localpath'] = ''
						prResolveFromCodeInfoDict[bugid]['impact'] =''
						prResolveFromCodeInfoDict[bugid]['menutree_iamge'] =''
						prResolveFromCodeInfoDict[bugid]['suggestion'] = ''
                                                #add by zhaoshie 20150612
						prResolveFromCodeInfoDict[bugid]['rootcause'] = ''
						prResolveFromCodeInfoDict[bugid]['rootcauseDetail'] = ''
						prResolveFromCodeInfoDict[bugid]['Solution'] = ''
						prResolveFromCodeInfoDict[bugid]['persoregen'] = 'Unknown'
						prResolveFromCodeInfoDict[bugid]['assign_department'] = i.created_user.fullname
						##end add by laiyinfang 2014-04-16
						continue
					if re.search(sw_release,ALMswRelease) or re.search(sw_release2,ALMswRelease) or self.SWRelease_mini_check(ALMswRelease) or (i.type=="Task"): 
						prVeriSWOldResolveInfoDict[bugid] = {}
						prVeriSWOldResolveInfoDict[bugid]['type'] = i.type
						prVeriSWOldResolveInfoDict[bugid]['reporter'] = self.creat_email(i)
						prVeriSWOldResolveInfoDict[bugid]['status'] = i.state
						prVeriSWOldResolveInfoDict[bugid]['ownerinfo'] = self.assigned_email(i)
						prVeriSWOldResolveInfoDict[bugid]['function'] = i.function
						prVeriSWOldResolveInfoDict[bugid]['milestone'] = i.new_ref
						prVeriSWOldResolveInfoDict[bugid]['desc'] = i.summary
						prVeriSWOldResolveInfoDict[bugid]['commentcea'] = i.all_cea_comments
						prVeriSWOldResolveInfoDict[bugid]['impact'] = ''
						prVeriSWOldResolveInfoDict[bugid]['menutree_iamge'] = ''
						prVeriSWOldResolveInfoDict[bugid]['suggestion'] = ''
                                                #add by zhaoshie 20150612
						prVeriSWOldResolveInfoDict[bugid]['rootcause'] = ''
						prVeriSWOldResolveInfoDict[bugid]['rootcauseDetail'] = ''
						prVeriSWOldResolveInfoDict[bugid]['Solution'] = ''
						prVeriSWOldResolveInfoDict[bugid]['persoregen'] = 'Unknown'
						prVeriSWOldResolveInfoDict[bugid]['assign_department'] = i.created_user.fullname
						self.needDeliverPR = True
			

	def deliverPRlist(self, conf, prVeriSWFromCodeInfoDict, prVeriSWOldResolveInfoDict,curVerTimeStr,NeedDeliveredButNotDeliveredBugs,prResolveFromCodeInfoDict):

		print "Now start to get all bugs need delivered"
		##add and modified by renzhi.yang 15-1-13
		tempversion = conf.getConf('tempversion','the version is temp version or not<yes|no>','no')
		if self.needDeliverPR and conf.getConf('delivresprweb', 'Deliver RESOLVED PR in Bugzilla <yes|no>', 'yes' if conf.getConf('isBigVersion', 'version is big version') == 'yes' and conf.getConf('sendto', 'email sendto<all|self>') == 'all' and tempversion == 'no' else 'no') == 'yes':
		##end by renzhi.yang
			prNeedDelivHash = {}
			for bugid,buginfo in prVeriSWFromCodeInfoDict.items():
				# modify by renzhi 2016.1.6
				#if buginfo['status'] in ['Verified_SW', 'Delivered'] and self.ifDeliverCodeLoadPR(conf,bugid) and self.getPRVerify_sw_Time(conf,bugid,curVerTimeStr):
				if buginfo['status'] in ['Verified_SW', 'Delivered'] and self.getPRVerify_sw_Time(conf,bugid,curVerTimeStr):
				# end 2016.1.6
					prNeedDelivHash[bugid] = [buginfo['status'], buginfo['milestone']]
					prVeriSWFromCodeInfoDict[bugid]['status'] = 'Delivered'
				else:
					if bugid not in prResolveFromCodeInfoDict.keys():
						prResolveFromCodeInfoDict[bugid] = buginfo
						del prVeriSWFromCodeInfoDict[bugid]
					
					
			for bugid,buginfo in prVeriSWOldResolveInfoDict.items():
				print "veri sw old resovle pr ------ %s" % bugid
				if buginfo['status'] in ['Verified_SW', 'Delivered']  and self.getPRVerify_sw_Time(conf,bugid,curVerTimeStr):
					prNeedDelivHash[bugid] = [buginfo['status'], buginfo['milestone']]
					prVeriSWOldResolveInfoDict[bugid]['status'] = 'Delivered'
				else:
					if bugid not in prResolveFromCodeInfoDict.keys():
						prResolveFromCodeInfoDict[bugid] = buginfo
						del prVeriSWOldResolveInfoDict[bugid]
			print "The all need delivered bugs are %s" % prNeedDelivHash.keys()
			self.deliverPR(conf, prNeedDelivHash)
			self.checkPRStatus(conf,prVeriSWFromCodeInfoDict,prVeriSWOldResolveInfoDict,NeedDeliveredButNotDeliveredBugs)
		curRow = 4


	#add by yrz to check bug status after deliverd
	def checkPRStatus(self, conf, prVeriSWFromCodeInfoDict, prVeriSWOldResolveInfoDict,NeedDeliveredButNotDeliveredBugs):
		print "Now start to filter no delivered bugs"
		for bugid,buginfo in prVeriSWFromCodeInfoDict.items():
			tmpList = self.db_conn.getItemsByCustomQuery(fields=['State'], query="(field[ID]= %s)" % bugid)
			if tmpList and (not tmpList[0].state == 'Delivered'):
				if bugid not in NeedDeliveredButNotDeliveredBugs.keys():
					buginfo['status'] = tmpList[0].state
					NeedDeliveredButNotDeliveredBugs[bugid] = buginfo
					del prVeriSWFromCodeInfoDict[bugid]
					

		for bugid,buginfo in prVeriSWOldResolveInfoDict.items():
			tmpList = self.db_conn.getItemsByCustomQuery(fields=['State'], query="(field[ID]= %s)" % bugid)
			if tmpList and (not tmpList[0].state == 'Delivered'):
				if bugid not in NeedDeliveredButNotDeliveredBugs.keys():
					buginfo['status'] = tmpList[0].state
					NeedDeliveredButNotDeliveredBugs[bugid] = buginfo
					del prVeriSWOldResolveInfoDict[bugid]	
	#end by yrz 2015-12-4
	
	#add by lyf 2015-06-09
	def getPRVerify_sw_Time(self, conf, bugid, curVerTimeStr):
		Item = self.db_conn.getItemsByCustomQuery(fields=['Last Verified_SW Date'], query="(field[ID] = %s)" %bugid )
                verified_sw_date = Item[0].last_verified_sw_date
                return self.compare_two_time(verified_sw_date,curVerTimeStr) #true,verified_sw_date(defect verified time) < curVerTimeStr(int time)
	#add by lyf 2015-06-09

	def checkCodeLoadPR(self, version, base, tempdir, sendTo, info, bugid):
		return True

	## check manual change PR, you must override this method
	def checkManualChangePR(self, conf, bugid, branchName):
		version = conf.getConf('version', 'project current version')
		branch = conf.getConf('projbugbranch','bugzilla branch','')
		branchArr = branch.split(',')
		if version[0:3] == conf.getConf('versionX','xls table versionX')[0:3] and branchName in branchArr:
			print "bug id------------------> %d"%bugid
			return True
		else :
			print "bug id------------------> %d"%bugid
			print "not right branch------------------> %s"%branchName
			return False

	## deliver code load PR
	def ifDeliverCodeLoadPR(self, conf, bugid):
		tmpList = self.db_conn.getItemsByCustomQuery(fields=['singleBranch','ID'], query="(field[ID]= %s)" % bugid)
		version = conf.getConf('version', 'project current version')
		branch = conf.getConf('projbugbranch','bugzilla branch','')
		branchArr = branch.split(',')
		if version[0:3] == conf.getConf('versionX','xls table versionX')[0:3] and tmpList[0].branch in branchArr:
			print "bug id------------------> %d"%tmpList[0].ID.integer.value
			return True
		else :
			print "bug id------------------> %d"%tmpList[0].ID.integer.value
			print "branch------------------> %s"%tmpList[0].branch
			return False

	## get bugzilla product id
	def getBugzillaProduct(self, conf):
		return re.findall('[^,]+', conf.getConf('bugzillaproductid', 'Product id in bugzilla'))

	### deliver PR status from browser user mechanize
	def deliverPR(self, conf, prHash):
		print "Now start to delivered verified_sw bugs"
		countPRNeedDeliver = 0
		curPRDeliverNumber = 1
		isLogedInBugzilla = False
		for pr,infoList in prHash.items():
			if infoList[0] in ['Verified_SW', 'Delivered']:
				countPRNeedDeliver += 1
		print 'CAUTION: %d PRs are to be delivered or be added comment' % countPRNeedDeliver
		for pr,infoList in prHash.items():
			if infoList[0] in ['Verified_SW', 'Delivered']:
				if not isLogedInBugzilla:
					while True:
						self.almlogname = conf.getConf('almloginname', 'ALM loggin name', ask=2)
						self.almpaword = conf.getConf('almpassword', 'ALM password', ask=2, echo=False)
						self.get_db_connection_for_delivered(self.almlogname,self.almpaword)			
						print "The value of login is %s" % self.login
						if re.match('^sucess$',self.login):
							print "Login ALM ok"
							break	
						elif re.match('^fail$',self.login):
							print "Login ALM fail, try again..."
					isLogedInBugzilla = True
				try:
					version = conf.getConf('version','current version')
					verstr = 'SW%s' % version
					fullName = conf.getConf('almloginname', 'almloginname', 'hudson.admin')
					comment = 'The new ref is updated by %s with int tool superspam\n' % fullName
					if infoList[0] == 'Verified_SW':
						comment += 'Change bug status to DELIVERED\n'						
					comment += 'New ref: %s' % verstr
					comment += '\nPlease use %s to verify' % verstr
                        		new_ref = verstr
					print "The bugid is %s" % pr
					print "The new ref is %s" % new_ref
					print "The comment is %s" % comment    			
					self.db_conn.editItem(item_id = pr, **{'New Ref':new_ref,'Additional Comments':comment,'State':'Delivered'})
				except Exception, e:
					print e
					print 'WARNING: Deliver PR %s fail, please check' % str(pr)
					
			else:
				pass				
		
	def compare_time(self,l_time,start_t,end_t):
		s_time = time.mktime(time.strptime(start_t,'%Y-%m-%d %H:%M:%S')) # get the seconds for specify date
		e_time = time.mktime(time.strptime(end_t,'%Y-%m-%d %H:%M:%S'))
		log_time = time.mktime(time.strptime(l_time,'%Y-%m-%d %H:%M:%S'))
		if (float(log_time) >= float(s_time)) and (float(log_time) <= float(e_time)):
			return True
		return False

	def compare_two_time(self,start_t,end_t):
		s_time = time.mktime(time.strptime(start_t,'%Y-%m-%d %H:%M:%S')) # get the seconds for specify date
		e_time = time.mktime(time.strptime(end_t,'%Y-%m-%d %H:%M:%S'))		
		if (float(s_time) < float(e_time)):
			return True
		return False

	def create_releasenote(self, conf):		
		#projects = self.getproject()
		for productIdStr in self.getBugzillaProduct(conf):
			if not re.match('\d+', productIdStr):
				project = productIdStr
			else:
				for i in self.projects:
					if productIdStr == i.ID:
						project = i.Name
						break
		branch = conf.getConf('projbugbranch', 'project bugbranch',' ')		
		state = "Active"
		version = conf.getConf('version', 'current version')
		version = 'SW%s' % version
	
		if self.almlogname:		
			print "You have logined ALM"
		else:
			self.almlogname = conf.getConf('almloginname', 'ALM loggin name', ask=2)
			self.almpaword = conf.getConf('almpassword', 'ALM password', ask=2, echo=False)
			print "You logined in ALM just now"	
		try:
			common.show("%s Connect to alm" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
			self.db_conn = IntegrityClient(self.url, credential_username='hz.int', credential_password='ptc')
		except Exception, e:
			print e
			print "Login ALM fail ,try again..."
				
		#self.db_conn = IntegrityClient(self.url, credential_username=self.almlogname, credential_password=self.almpaword)
		self.db_conn.createReleaseNote(State=state,InProject=project,Branch=branch,Version=version)
		match = re.search('\/.*\/(.*)\/', project)
		project_gapp = project
		project_gapp = project_gapp.replace(match.group(1),"Others")
		project_gapp = project_gapp + " for GAPP"
		print "The gapp projetc name is %s" % project_gapp
		#projects = self.getproject()
		for item in self.projects:
			if item.Name == project_gapp:
				print "The Gapp name of projetc is existing %s" % project_gapp
				print "state:%s,projectname:%s,branch:%s,version:%s" % (state,project_gapp,branch,version)
				self.db_conn.createReleaseNote(State=state,InProject=project_gapp,Branch=branch,Version=version)
				break



	### get all delivered defect of the project
	##  add by renzhi.yang 2015-1-29
	def getAllDeliveredDefectInfoDict(self, productIdNumList,AllDeliveredDefectInfoDict, conf):
		productIdSqlList = []
		#projects = self.getproject()
		for oneProductIdNum in productIdNumList:
			for i in self.projects:			
				if  i.ID == oneProductIdNum:		
					productIdNumStr = i.Name								
					productIdSqlList.append('%s' % productIdNumStr)
					break
		State = "Delivered"
		for i in productIdSqlList:
                        count = 0	
                        while count < 3:
                               try:
                                     print "begin to get %s %s Defect Info" % (i, State)	
                                     mysqlCursor = self.db_conn.getItemsByCustomQuery(fields=['ID','Type','Created By','State','Function','New Ref','Summary','All CEA comments','Assigned User','Resolution','Reporter Department'], query="((field[State] = %s) and (field[In Project] = %s) and (field[Type] = Defect))" % (State,i))
                                     break
                               except Exception, e:
                                     if count > 2:
					print e
					break
                                     else:
					self.db_conn = IntegrityClient(self.url,
					credential_username="hz.int",
					credential_password="ptc")
                                        count += 1
                    			continue
			NumOfBugs = len(mysqlCursor)
			if not NumOfBugs:
				continue
			for i in mysqlCursor:
				bugid = i.ID.integer.value
				if bugid in AllDeliveredDefectInfoDict.keys():
					continue
				AllDeliveredDefectInfoDict[bugid] = {}
				AllDeliveredDefectInfoDict[bugid]['type'] = i.type
				AllDeliveredDefectInfoDict[bugid]['reporter'] = self.creat_email(i)
				AllDeliveredDefectInfoDict[bugid]['status'] = i.state
				AllDeliveredDefectInfoDict[bugid]['ownerinfo'] = self.assigned_email(i)
				AllDeliveredDefectInfoDict[bugid]['function'] = i.function
				AllDeliveredDefectInfoDict[bugid]['milestone'] = i.new_ref
				AllDeliveredDefectInfoDict[bugid]['desc'] = i.summary
				AllDeliveredDefectInfoDict[bugid]['commentcea'] = i.all_cea_comments
				AllDeliveredDefectInfoDict[bugid]['assign_department'] = i.created_user.fullname
	
	### get defect's type and status
	##  add by shie.zhao 2015-1-29
	def getDefectTypeStatus(self, bugid):
		#projects = self.getproject()
                bugType = ''
		bugState = ''
                count = 0 
                while count < 3:
                    try:
                        print "Begin to get %s type and state" % bugid
		        items = self.db_conn.getItemsByCustomQuery(fields=['ID','Type','State'], query="((field[ID]=%s))" % bugid )  
                        break
                    except Exception, e:
			if count > 2:
		             print e
		             break
			else:
		             self.db_conn = IntegrityClient(self.url,
		             credential_username="hz.int",
		             credential_password="ptc")
                             count += 1
		             continue  
     
                bugType = items[0].type
                bugState = items[0].state
                #print "Type of %s is %s,and state of %s is %s" %(bugid,bugType,bugid,bugState)
		return bugType,bugState

	def getAllDeliveredFRBranchInfoDict(self, productIdNumList,AllDeliveredFRInfoDict, conf):
		productIdSqlList = []
		bugBranch = conf.getConf('projbugbranch', 'project bugbranch',' ')
		branchArr = bugBranch.replace(',',"','")
		#projects = self.getproject()
                count = 0
		for oneProductIdNum in productIdNumList:
			for i in self.projects:			
				if  i.ID == oneProductIdNum:		
					productIdNumStr = i.Name								
					productIdSqlList.append('%s' % productIdNumStr)
					break
		Stat = "Delivered"
		for project in productIdSqlList:
                        count = 0
                        while count < 3:
                            try:	
                                  print "begin to get %s FR branch from %s by ALM" % (Stat,project)	
			          mysqlCursor = self.db_conn.getItemsByCustomQuery(fields=['ID','Type','Created By','State','singleBranch','Summary','Assigned User','FR ID'], query="((field[State] = %s) and (field[Project] = %s) and (field[Type] = FR branch))" % (Stat,project))
                                  break
                            except Exception, e:
				  if count > 2:
					print e
					break
                		  else:
					self.db_conn = IntegrityClient(self.url,
					credential_username="hz.int",
					credential_password="ptc")
                                        count += 1
                    			continue

			NumOfBugs = len(mysqlCursor)
			print NumOfBugs
			if not NumOfBugs:
				continue			
			for item in mysqlCursor:
				if item and (item.branch in branchArr):
					FRid = item.ID.integer.value
					if FRid in AllDeliveredFRInfoDict.keys():
						continue
					AllDeliveredFRInfoDict[FRid] = {}
					AllDeliveredFRInfoDict[FRid]['type'] = item.type
					AllDeliveredFRInfoDict[FRid]['status'] = item.state
					AllDeliveredFRInfoDict[FRid]['branch'] = item.branch				
					AllDeliveredFRInfoDict[FRid]['desc'] = item.summary
					AllDeliveredFRInfoDict[FRid]['generalFRID'] = item.related_fr_id

    #add for reqirement for ongoing pr list begin 01-12-2015 by INT
	def getOGPRDict(self,conf,productIdNumList,OGPRTitleList,prOGFromDBDict,OGHomoDefectDict):
		bugBranch = conf.getConf('projbugbranch', 'project bugbranch','TBD')
		branchArr = bugBranch.replace(',',"','")
		#projects = self.getproject()
                count=0
		productIdSqlList = []		
		for oneProductIdNum in productIdNumList:
			for i in self.projects:			
				if  i.ID == oneProductIdNum:		
					productIdNumStr = i.Name								
					productIdSqlList.append('%s' % productIdNumStr)
					break	
		for title in OGPRTitleList:
			prOGFromDBDict[title] = 0
		for i in productIdSqlList: 
                        count = 0                       
	                while count < 3:
			   try:
                                print "begin to get Ongoing defect and task from %s" %i	
				mysqlCursor = self.db_conn.getItemsByCustomQuery(fields=['ID','Type','Priority','Created By','State','singleBranch','IPR Value','Assigned User','Resolution','Homo','Assignee Department'], query="(((field[State]=New,Assigned,Opened) or ((field[State]= Verified_SW) and (field[Resolution] = Refused))) and (field[Project] = %s) and (field[Type]= Defect,Task))" % i)
               			break
            		   except Exception, e:
				if count > 2:
					print e
					break
                		else:
					self.db_conn = IntegrityClient(self.url,
					credential_username="hz.int",
					credential_password="ptc")
                                        count += 1
                    			continue                       
			NumOfBugs = len(mysqlCursor)				
			if not NumOfBugs:
				continue			
			for item in mysqlCursor:
				if item and (item.branch in branchArr):
					if item.homo == 'YES':
						bugid = item.id
						OGHomoDefectDict[bugid] = {}
						OGHomoDefectDict[bugid]['Type'] = item.type
						OGHomoDefectDict[bugid]['CU_REF'] = item.cu_ref
						OGHomoDefectDict[bugid]['REPORTER'] = self.creat_email(item)
						OGHomoDefectDict[bugid]['STATUS'] = item.state
						OGHomoDefectDict[bugid]['OWNER'] = self.assigned_email(item)
						OGHomoDefectDict[bugid]['FUNCTION'] = item.function
						OGHomoDefectDict[bugid]['SHORT_DESC'] = item.summary
						OGHomoDefectDict[bugid]['CF_COMMENT_CEA'] = item.all_cea_comments
						OGHomoDefectDict[bugid]['COMPONENT'] = item.compone							
					if item.priority == 'P0 (Urgent)':
						prOGFromDBDict['P0_OG'] += 1
					elif item.priority == 'P1 (Quick)' and item.ipr_value > 300:
						prOGFromDBDict['P1_IPR_300_OG'] += 1
					else:
						prOGFromDBDict['OTHERS_OG'] += 1
					if self.assigned_email(item):
						if self.adjustAssingerDp(item.assignee_pepartment):
							prOGFromDBDict['INTERNAL_OG_TOTAL'] += 1
						else:
							prOGFromDBDict['EXTERNAL_OG_TOTAL'] += 1
		sum = prOGFromDBDict['P0_OG']+prOGFromDBDict['P1_IPR_300_OG']+prOGFromDBDict['OTHERS_OG']
		if sum == prOGFromDBDict['INTERNAL_OG_TOTAL'] + prOGFromDBDict['EXTERNAL_OG_TOTAL']:
			prOGFromDBDict['TOTAL_OG'] = sum

	#add for filter SW release
	def getSwRelease(self,conf):
		version = conf.getConf('version', 'project current version')
		match = re.match(('^.{3}'),version)
		if match:
			sw_release = match.group(0)
			sw_release = sw_release.upper()
			#add for 15-4-3
			print "sw_release is %s" % sw_release
			if sw_release == "5E3":
				re_release2 = "5E2"
			elif sw_release == "5E2":
				re_release2 = "5E1"
			elif sw_release == "BL2":
				re_release2 = "BL1"
			elif sw_release == "6F2":
				re_release2 = "6F1"
			else:
				re_release2 = "no"				
		
		else:
			sw_release = ''
		return sw_release,re_release2

	def SWRelease_mini_check(self, swRelease):
		match = re.match('SW(.*)', swRelease)
		if match:
			version = match.group(1)
			if self.isMiniVersion(version) == 'yes':
				print "This defect's SW_Release is MINI version"
				return True
		else:
			return False
		

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
			
	def getAllDeliveredFRWithoutFRBranchInfoDict(self, productIdNumList,AllDeliveredFRWithoutFrBranch, conf):
		productIdSqlList = []
		bugBranch = conf.getConf('projbugbranch', 'project bugbranch',' ')
		branchArr = bugBranch.replace(',',"','")
                count = 0
		#projects = self.getproject()
		for oneProductIdNum in productIdNumList:
			for i in self.projects:			
				if  i.ID == oneProductIdNum:		
					productIdNumStr = i.Name								
					productIdSqlList.append('%s' % productIdNumStr)
					break
		Stat = "Delivered"
		for project in productIdSqlList:
                        count = 0 
                        while count < 3: 
                            try:
                                   print "begin to get %s General FR from %s " % (Stat,project)			
			           mysqlCursor = self.db_conn.getItemsByCustomQuery(fields=['ID','Type','Created By','State','singleBranch','Summary','Assigned User','FR Relate Branch(QBR)'], query="((field[State] = %s) and (field[Project] = %s) and (field[Type] = General FR))" % (Stat,project))
                                   break
                            except Exception, e:
				   if count > 2:
					print e
					break
                		   else:
					self.db_conn = IntegrityClient(self.url,
					credential_username="hz.int",
					credential_password="ptc")
                                        count += 1
                    			continue



			NumOfBugs = len(mysqlCursor)
			print NumOfBugs
			if not NumOfBugs:
				continue			
			for item in mysqlCursor:
				if item and (not item.fr_relate_branch) and (item.branch in branchArr):
					FRid = item.ID.integer.value
					if FRid in AllDeliveredFRWithoutFrBranch.keys():
						continue
					AllDeliveredFRWithoutFrBranch[FRid] = {}
					AllDeliveredFRWithoutFrBranch[FRid]['type'] = item.type
					AllDeliveredFRWithoutFrBranch[FRid]['status'] = item.state
					AllDeliveredFRWithoutFrBranch[FRid]['branch'] = item.branch				
					AllDeliveredFRWithoutFrBranch[FRid]['desc'] = item.summary
					AllDeliveredFRWithoutFrBranch[FRid]['reporter'] = self.creat_email(item)
					AllDeliveredFRWithoutFrBranch[FRid]['ownerinfo'] = self.assigned_email(item)

	def diffDefectAndTask(self, prVeriSWFromCodeInfoDict,prVeriSWOldResolveInfoDict, prResolveFromCodeInfoDict,taskVeriSWFromCodeInfoDict,taskVeriSWOldResolveInfoDict):
		for bugid in sorted(prVeriSWFromCodeInfoDict.keys()):
			if prVeriSWFromCodeInfoDict[bugid]['type'] == "Task":
				if bugid not in taskVeriSWFromCodeInfoDict.keys():
					taskVeriSWFromCodeInfoDict[bugid] = prVeriSWFromCodeInfoDict[bugid]
				del prVeriSWFromCodeInfoDict[bugid]

		for bugid in sorted(prVeriSWOldResolveInfoDict.keys()):
			if prVeriSWOldResolveInfoDict[bugid]['type'] == "Task":
				if bugid not in taskVeriSWOldResolveInfoDict.keys():
					taskVeriSWOldResolveInfoDict[bugid] = prVeriSWOldResolveInfoDict[bugid]
				del prVeriSWOldResolveInfoDict[bugid]

	def getFRBranchOFCurDict(self, conf, DeliveredFROFCurrentVersion, lastVerTimeStr, curVerTimeStr):
		bugBranch = conf.getConf('projbugbranch', 'project bugbranch','TBD')
		branchArr = bugBranch.replace(',',"','")
		or_query = ' or '.join(['(field[Project]=%s)' % project for project in self.getBugzillaProduct(conf)]) 
		lastVerTime = self.convertToDatetime(lastVerTimeStr)
		curVerTime = time.strftime('%b %d, %Y %I:%M:%S %p',time.localtime(time.time()))
		time_query = '(field[Last delivered time] between time %s and %s)' % (lastVerTime, curVerTime)
		query = "((field[State] = Delivered) and (field[Type] = FR branch) and %s and %s)" % (or_query,time_query)
		count = 0
		FR_Branchs = []
		while count < 3:
			try:
                                print "begin to get %s by ALM" %query
				FR_Branchs = self.db_conn.getItemsByCustomQuery(fields=['ID', 'Type', 'Created By', 'State', 'Summary', 'Assigned User', 'FR ID'], query=query)
               			break
            		except Exception, e:
				if count > 2:
					print e
					break
                		else:
					self.db_conn = IntegrityClient(self.url,
					credential_username="hz.int",
					credential_password="ptc")
                                        count += 1
                    			continue
        	for frbranch in FR_Branchs:
			if not frbranch:
				continue
        		bugid = frbranch.id
			if frbranch.branch in branchArr:
        			DeliveredFROFCurrentVersion[bugid] = {}
        			DeliveredFROFCurrentVersion[bugid]['type'] = frbranch.type
        			DeliveredFROFCurrentVersion[bugid]['branch'] = frbranch.branch
        			DeliveredFROFCurrentVersion[bugid]['status'] = frbranch.state
				RelatedFrID = frbranch['FR ID'][1].value if 'FR ID' in frbranch.keys() else ''					
        			DeliveredFROFCurrentVersion[bugid]['releatedId'] = RelatedFrID
        			DeliveredFROFCurrentVersion[bugid]['desc'] = frbranch.summary
        			DeliveredFROFCurrentVersion[bugid]['reporter'] = self.GetRelatedFRID_of_FRBranch(RelatedFrID)

	def GetRelatedFRID_of_FRBranch(self,RelatedFrID):
		reportFullName = ''
                count = 0
		if RelatedFrID:
                        while count < 3:
                             try:
                                  #print "begin to get %s of FRBranch by ALM" % RelatedFrID
			          mysqlCursor = self.db_conn.getItemsByCustomQuery(fields=['Type','Created By'], query="(field[ID] = %s)" % RelatedFrID)
                                  break
                             except Exception, e:
                                  if count > 2:
					print e
					break
                                  else:
					self.db_conn = IntegrityClient(self.url,
					credential_username="hz.int",
					credential_password="ptc")
                                        count += 1
                    			continue			
			reportFullName = mysqlCursor[0].created_user.fullname
		return reportFullName			
				
	def convertToDatetime(self, str):
		if str:
			datime = datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y %I:%M:%S %p')
		else:
			datime = ''
		return datime



	def getBranchName(self, branchID):
		branchName = ''
		if branchID:
			branch = self.db_conn.getItemsByCustomQuery(fields=['ID','Summary'], query="(field[ID] = %s)" % branchID)
			branchName = branch[0]['Summary'].shorttext.value
		return branchName
		
