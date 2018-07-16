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
	bugzillaloginname = ''
	bugzillapassword = ''
	def getUserNameFromUid(self, uid, mysqlConn):
		cur = mysqlConn.cursor()
		cur.execute('SELECT realname,login_name FROM profiles WHERE userid=%s' % str(uid))
		res = cur.fetchone()
#        userName = '%s <%s>' % (res[0], res[1])
       		userName = res[1]
		cur.close()
		return userName
	
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
#			tmpList.append('%d) %s [%s]' % (nCount, self.getUserNameFromUid(resolve[0], mysqlConn), resolve[1]))
            		tmpList.append(self.getUserNameFromUid(resolve[0], mysqlConn))
		if tmpList:
			return '\r\n'.join(tmpList)
		else:
			#return '1) %s []' % self.getUserNameFromUid(assigned_to, mysqlConn)
           		return self.getUserNameFromUid(assigned_to, mysqlConn)

	def getFunctionName(self, funcId, mysqlConn):
		cur = mysqlConn.cursor()
		cur.execute('SELECT name FROM functions WHERE id=%s' % str(funcId))
		funcName = cur.fetchone()[0]
		cur.close()
		return funcName

	def getIDNumberAndCodeList(self, conf, productIdNumList, prFromCodeList, mysqlConn):
		for productIdStr in self.getBugzillaProduct(conf):
			if not re.match('\d+', productIdStr):
				mysqlCursor = mysqlConn.cursor()
				mysqlCursor.execute('SELECT id FROM products WHERE name="%s"' % productIdStr)
				productIdNumStr = str(mysqlCursor.fetchone()[0])
				mysqlCursor.close()
			else:
				productIdNumStr = productIdStr
			productIdNumList.append(int(productIdNumStr))

		for bugid in self.prFromCodeDict.keys():
			mysqlCursor = mysqlConn.cursor()
			mysqlCursor.execute('SELECT product_id FROM bugs WHERE bug_id=%d' % bugid)
			resList = mysqlCursor.fetchone()
			mysqlCursor.close()
			if not resList:
				continue
			curBugProductId = resList[0]
			if not curBugProductId in productIdNumList:
				continue
			#if self.checkCodeLoadPR(version, base, tempdir, sendTo, info, mysqlConn, bugid):
			prFromCodeList.append(bugid)
		prFromCodeList.sort()

	## get VERIFIED_SW and RESOLVED PR 
	def getSWAndRelPRList(self, conf, mysqlConn, prFromCodeList, prVeriSWFromCodeInfoDict, prResolveFromCodeInfoDict, curVerTimeStr, lastVerTimeStr):
		bugBranch = conf.getConf('projbugbranch', 'project bugbranch','TBD')
		branchArr = bugBranch.replace(',',"','")
		for bugid in prFromCodeList:
			mysqlCursor = mysqlConn.cursor()
			mysqlCursor.execute('SELECT bug_id,bug_type,reporter,bug_status,function_id,target_milestone,short_desc,cf_comment_cea,assigned_to,resolution FROM bugs WHERE bug_id=%d and cf_branch in %s' % (bugid, "('"+branchArr+"')"))
			resList = mysqlCursor.fetchone()
			if not resList:
				continue
			if (resList[3] == 'VERIFIED_SW' and resList[9] in ['Validated', "Can't test", "Monitor"]) or resList[3] == 'DELIVERED':
                                ##  begin modify by zhaoshie 2015-01-6 for checking verify_sw time
                                tmpCursor = mysqlConn.cursor()
                             	tmpCursor.execute('SELECT bug_when FROM bugs_activity WHERE bug_id=%d AND added="VERIFIED_SW" ORDER BY bug_when DESC' % bugid)
				tmpResList = tmpCursor.fetchone()
				if tmpResList:
					match=re.match('(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+)', curVerTimeStr)
					if datetime.datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), int(match.group(5)), int(match.group(6))) >= tmpResList[0]:
                               ##  end modify by zhaoshie 2015-01-6 for checking verify_sw time
				              prVeriSWFromCodeInfoDict[bugid] = {}
				              prVeriSWFromCodeInfoDict[bugid]['type'] = resList[1]
				              prVeriSWFromCodeInfoDict[bugid]['reporter'] = self.getUserNameFromUid(resList[2], mysqlConn)
				              prVeriSWFromCodeInfoDict[bugid]['status'] = resList[3]
				              prVeriSWFromCodeInfoDict[bugid]['ownerinfo'] = self.getOwnerInfo(bugid, lastVerTimeStr, curVerTimeStr, mysqlConn, resList[8])
				              prVeriSWFromCodeInfoDict[bugid]['function'] = self.getFunctionName(resList[4], mysqlConn)
				              prVeriSWFromCodeInfoDict[bugid]['milestone'] = resList[5]
				              prVeriSWFromCodeInfoDict[bugid]['desc'] = resList[6]
				              prVeriSWFromCodeInfoDict[bugid]['commentcea'] = resList[7]
				              prVeriSWFromCodeInfoDict[bugid]['localpath'] = self.prFromCodeDict[bugid]['localPath']
				              prVeriSWFromCodeInfoDict[bugid]['impact'] = self.prFromCodeDict[bugid]['moduleImpact'].decode('utf8')
				              prVeriSWFromCodeInfoDict[bugid]['menutree_iamge'] = self.prFromCodeDict[bugid]['menutree_iamge'].decode('utf8')
				              prVeriSWFromCodeInfoDict[bugid]['suggestion'] = self.prFromCodeDict[bugid]['testSuggestion'].decode('utf8')
                                              #add by zhaoshie 20150612
				              prVeriSWFromCodeInfoDict[bugid]['rootcause'] = self.prFromCodeDict[bugid]['rootcause'].decode('utf8')
				              prVeriSWFromCodeInfoDict[bugid]['rootcauseDetail'] = self.prFromCodeDict[bugid]['rootcauseDetail'].decode('utf8')
				              prVeriSWFromCodeInfoDict[bugid]['Solution'] = self.prFromCodeDict[bugid]['Solution'].decode('utf8')
				              prVeriSWFromCodeInfoDict[bugid]['persoregen'] = 'Unknown'
				              if resList[3] == 'VERIFIED_SW':
					            self.needDeliverPR = True
			if resList[3] == 'RESOLVED':
				prResolveFromCodeInfoDict[bugid] = {}
				prResolveFromCodeInfoDict[bugid]['type'] = resList[1]
				prResolveFromCodeInfoDict[bugid]['reporter'] = self.getUserNameFromUid(resList[2], mysqlConn)
				prResolveFromCodeInfoDict[bugid]['status'] = resList[3]
				prResolveFromCodeInfoDict[bugid]['ownerinfo'] = self.getOwnerInfo(bugid, lastVerTimeStr, curVerTimeStr, mysqlConn, resList[8])
				prResolveFromCodeInfoDict[bugid]['function'] = self.getFunctionName(resList[4], mysqlConn)
				if resList[5]:
					prResolveFromCodeInfoDict[bugid]['milestone'] = resList[5]
				else:
					prResolveFromCodeInfoDict[bugid]['milestone'] = 'N/A'
				prResolveFromCodeInfoDict[bugid]['desc'] = resList[6]
				prResolveFromCodeInfoDict[bugid]['commentcea'] = resList[7]
				prResolveFromCodeInfoDict[bugid]['localpath'] = self.prFromCodeDict[bugid]['localPath']
				prResolveFromCodeInfoDict[bugid]['impact'] = self.prFromCodeDict[bugid]['moduleImpact'].decode('utf8')
				prResolveFromCodeInfoDict[bugid]['menutree_iamge'] = self.prFromCodeDict[bugid]['menutree_iamge'].decode('utf8')
				prResolveFromCodeInfoDict[bugid]['suggestion'] = self.prFromCodeDict[bugid]['testSuggestion'].decode('utf8')
                                #add by zhaoshie 20150612
				prResolveFromCodeInfoDict[bugid]['rootcause'] = self.prFromCodeDict[bugid]['rootcause'].decode('utf8')
				prResolveFromCodeInfoDict[bugid]['rootcauseDetail'] = self.prFromCodeDict[bugid]['rootcauseDetail'].decode('utf8')
				prResolveFromCodeInfoDict[bugid]['Solution'] = self.prFromCodeDict[bugid]['Solution'].decode('utf8')

				prResolveFromCodeInfoDict[bugid]['persoregen'] = 'Unknown'
                		#if self.sendrelv and conf.getConf('isBigVersion', 'version is big version') == 'yes':
				#removed by renzhi 2015-4-2
				#if conf.getConf('isBigVersion', 'version is big version') == 'yes':
                    			#self.prResolveInfoDict[bugid]=prResolveFromCodeInfoDict[bugid]
                    		#if prResolveFromCodeInfoDict[bugid]['ownerinfo'].__contains__("\n"):
                        			#self.prResolveInfoDict[bugid]['ownerinfo'] = self.getUserNameFromUid(resList[8], mysqlConn)
				#end by renzhi 2015-4-2
			mysqlCursor.close()


	def getPrSWAndRelOnOtherDict(self, conf, mysqlConn,lastVerTimeStr, curVerTimeStr):
		bugBranch = conf.getConf('projbugbranch', 'project bugbranch','TBD')
        	branchArr = bugBranch.replace(',',"','")
        	otherBranchDict = {}
        	try:
			config = ConfigParser()
			filepath  = os.path.realpath(__file__)
			config.read(filepath[:filepath.index("lib")]+'conf/prInOtherBranch.conf')
			projectname = conf.getConf('releasenoteprojname', 'Project name in release note')
			curBugBranch = config.get(projectname,'curBugBranch')
			if curBugBranch == bugBranch or curBugBranch in bugBranch.split(","):
				self.releaseBugBranchs = config.get(projectname,'releaseBugBranch').split(",")
			else:
				self.releaseBugBranchs = None
		except:
			self.releaseBugBranchs = None
		if self.releaseBugBranchs:
			for releaseBugBranch in self.releaseBugBranchs:
				prSWOnOtherDict = {}
				prRelOnOtherDict = {}
				mysqlCursor = mysqlConn.cursor()
#                mysqlCursor.execute("SELECT bugs.bug_id,bug_type,reporter,bug_status,function_id,target_milestone,short_desc,cf_comment_cea,assigned_to,resolution FROM bugs,bugs_activity WHERE bugs.bug_id = bugs_activity.bug_id AND cf_branch in ('pixi335-v1.0-dint-ssv')")
				mysqlCursor.execute("SELECT bugs.bug_id,bug_type,reporter,bug_status,function_id,target_milestone,short_desc,cf_comment_cea,assigned_to,resolution FROM bugs,bugs_activity WHERE bugs.bug_id = bugs_activity.bug_id AND (added = 'VERIFIED_SW' or added = 'RESOLVED') AND (bug_when > '%s' AND bug_when < '%s') AND cf_branch in %s" % (lastVerTimeStr,curVerTimeStr,"('"+releaseBugBranch+"')"))
			while True:
				resList = mysqlCursor.fetchone()
				if not resList:
					break
				bugid = resList[0]
#                    if resList[3] == 'CLOSED':
				if (resList[3] == 'VERIFIED_SW' and resList[9] in ['Validated', "Can't test"]) or resList[3] == 'DELIVERED':
					prSWOnOtherDict[bugid] = {}
					prSWOnOtherDict[bugid]['type'] = resList[1]
					prSWOnOtherDict[bugid]['reporter'] = self.getUserNameFromUid(resList[2], mysqlConn)
					prSWOnOtherDict[bugid]['status'] = resList[3]
					prSWOnOtherDict[bugid]['ownerinfo'] = self.getOwnerInfo(bugid, lastVerTimeStr, curVerTimeStr, mysqlConn, resList[8])
					prSWOnOtherDict[bugid]['function'] = self.getFunctionName(resList[4], mysqlConn)
					prSWOnOtherDict[bugid]['desc'] = resList[6]
					impact,sugges,rootcause,rootcauseDetail,Solution = self.getImpactAndSuges(bugid, mysqlConn, lastVerTimeStr, curVerTimeStr)
					prSWOnOtherDict[bugid]['impact'] = impact
					prSWOnOtherDict[bugid]['suggestion'] = sugges
                                        #add by zhaoshie 20150612
					prSWOnOtherDict[bugid]['rootcause'] = rootcause
					prSWOnOtherDict[bugid]['rootcauseDetail'] = rootcauseDetail
					prSWOnOtherDict[bugid]['Solution'] = Solution
				#else:
 				if resList[3] == 'RESOLVED':
					prRelOnOtherDict[bugid] = {}
					prRelOnOtherDict[bugid]['type'] = resList[1]
					prRelOnOtherDict[bugid]['reporter'] = self.getUserNameFromUid(resList[2], mysqlConn)
					prRelOnOtherDict[bugid]['status'] = resList[3]
					prRelOnOtherDict[bugid]['ownerinfo'] = self.getOwnerInfo(bugid, lastVerTimeStr, curVerTimeStr, mysqlConn, resList[8])
					prRelOnOtherDict[bugid]['function'] = self.getFunctionName(resList[4], mysqlConn)
					prRelOnOtherDict[bugid]['desc'] = resList[6]
					impact,sugges,rootcause,rootcauseDetail,Solution = self.getImpactAndSuges(bugid, mysqlConn, lastVerTimeStr, curVerTimeStr)
					prRelOnOtherDict[bugid]['impact'] = impact
					prRelOnOtherDict[bugid]['suggestion'] = sugges
                                        #add by zhaoshie 20150612
					prRelOnOtherDict[bugid]['rootcause'] = rootcause
					prRelOnOtherDict[bugid]['rootcauseDetail'] = rootcauseDetail
					prRelOnOtherDict[bugid]['Solution'] = Solution
				mysqlCursor.close()
			if prSWOnOtherDict.__len__() > 0 or prRelOnOtherDict.__len__() > 0:
				self.prSWAndRelOnOtherDict[releaseBugBranch] = (prSWOnOtherDict,prRelOnOtherDict)        
    #add for reqirement for ongoing pr list begin 01-12-2015 by INT
    #['P0_OG','P1_IPR_300_OG','OTHERS_OG','INTERNAL_OG_TOTAL','EXTERNAL_OG_TOTAL','TOTAL_OG']
	def getOGPRDict(self,conf,mysqlConn,productIdNumList,OGPRTitleList,prOGFromDBDict,curVerTimeStr,lastVerTimeStr):
		bugBranch = conf.getConf('projbugbranch', 'project bugbranch','TBD')
		branchArr = bugBranch.replace(',',"','")
		productIdSqlList = []
		for oneProductIdNum in productIdNumList:
			productIdSqlList.append('product_id=%d' % oneProductIdNum)
		for title in OGPRTitleList:
			prOGFromDBDict[title] = 0
		if curVerTimeStr:
			mysqlCursor = mysqlConn.cursor()
			mysqlCursor.execute("SELECT bug_id,assigned_to,bug_status,priority,cf_ipr FROM bugs WHERE (bug_status='NEW' OR bug_status='ASSIGNED' OR (bug_status='OPENED' AND resolution!='Refused') OR bug_status='INVESTIGATED' OR (bug_status='VERIFIED_SW' AND resolution='Refused'))  AND  (%s) AND cf_branch in %s" % (' OR '.join(productIdSqlList),"('"+branchArr+"')"))
		while True:
			line = mysqlCursor.fetchone()
			if not line:
				break
			if line[3] == 'P0 (Urgent)':
				prOGFromDBDict['P0_OG'] += 1
			elif line[3] == 'P1 (Quick)' and line[4] > 300:
				prOGFromDBDict['P1_IPR_300_OG'] += 1
			else:
				prOGFromDBDict['OTHERS_OG'] += 1
			if self.adjustSWReportPR(self.getLoginName(mysqlConn, line[1])):
				prOGFromDBDict['INTERNAL_OG_TOTAL'] += 1
			else:
				prOGFromDBDict['EXTERNAL_OG_TOTAL'] += 1
		mysqlCursor.close()
		sum = prOGFromDBDict['P0_OG']+prOGFromDBDict['P1_IPR_300_OG']+prOGFromDBDict['OTHERS_OG']
		if sum == prOGFromDBDict['INTERNAL_OG_TOTAL'] + prOGFromDBDict['EXTERNAL_OG_TOTAL']:
			prOGFromDBDict['TOTAL_OG'] = sum
    #add for reqirement for ongoing pr list begin 01-12-2015 by INT
	def getOGHomoDefect(self,conf,mysqlConn,productIdNumList,OGHomoDefectDict,curVerTimeStr,lastVerTimeStr):
		bugBranch = conf.getConf('projbugbranch', 'project bugbranch','TBD')
		branchArr = bugBranch.replace(',',"','")
		productIdSqlList = []
		for oneProductIdNum in productIdNumList:
			productIdSqlList.append('product_id=%d' % oneProductIdNum)
		if curVerTimeStr:
			mysqlCursor = mysqlConn.cursor()
			mysqlCursor.execute("SELECT bug_id,cf_cu_ref,reporter,bug_status,assigned_to,component_id,short_desc,function_id,cf_comment_cea FROM bugs WHERE cf_homo = 'yes' AND (bug_status='NEW' OR bug_status='ASSIGNED' OR bug_status='OPENED' OR bug_status='INVESTIGATED' OR bug_status='RESOLVED' OR (bug_status='VERIFIED_SW' AND resolution='Refused'))  AND  (%s) AND cf_branch in %s" % (' OR '.join(productIdSqlList),"('"+branchArr+"')"))
			while True:
				resList = mysqlCursor.fetchone()
				if not resList:
					break
				bugid = resList[0]
				OGHomoDefectDict[bugid] = {}
				OGHomoDefectDict[bugid]['CU_REF'] = resList[1]
				OGHomoDefectDict[bugid]['REPORTER'] = self.getUserNameFromUid(resList[2], mysqlConn)
				OGHomoDefectDict[bugid]['STATUS'] = resList[3]
				OGHomoDefectDict[bugid]['OWNER'] = self.getOwnerInfo(bugid, lastVerTimeStr, curVerTimeStr, mysqlConn, resList[4])
				OGHomoDefectDict[bugid]['FUNCTION'] = self.getFunctionName(resList[7], mysqlConn)
				OGHomoDefectDict[bugid]['SHORT_DESC'] = resList[6]
				OGHomoDefectDict[bugid]['CF_COMMENT_CEA'] = resList[8]
				cursor = mysqlConn.cursor()
				cursor.execute("select name from components where id=27696")
				OGHomoDefectDict[bugid]['COMPONENT'] = cursor.fetchone()[0]
				cursor.close()
			mysqlCursor.close()
	##  begin modify by laiyinfang 2014-04-16
	def getVeriSWOldResolveInfoDict(self, mysqlConn, productIdNumList, prVeriSWOldResolveInfoDict, prVeriSWFromCodeInfoDict,prResolveFromCodeInfoDict,curVerTimeStr, lastVerTimeStr, conf):
		## end modily by laiyinfang 2014-04-16
		productIdSqlList = []
		for oneProductIdNum in productIdNumList:
			productIdSqlList.append('product_id=%d' % oneProductIdNum)
		if curVerTimeStr:
			mysqlCursor = mysqlConn.cursor()
			mysqlCursor.execute('SELECT bug_id,bug_type,reporter,bug_status,function_id,target_milestone,short_desc,cf_comment_cea,assigned_to,resolution FROM bugs WHERE bug_status="VERIFIED_SW" AND (resolution="Validated" OR resolution="Can\'t test" OR resolution="Monitor") AND (%s)' % ' OR '.join(productIdSqlList))
			while True:
				resList = mysqlCursor.fetchone()
				if not resList:
					break
				bugid = resList[0]
				if bugid in prVeriSWFromCodeInfoDict.keys():
					continue
				if not self.checkManualChangePR(conf, mysqlConn, bugid):
					continue
				tmpCursor = mysqlConn.cursor()
				tmpCursor.execute('SELECT bug_when FROM bugs_activity WHERE bug_id=%d AND added="VERIFIED_SW" ORDER BY bug_when DESC' % bugid)
				tmpResList = tmpCursor.fetchone()
				if tmpResList:
					match=re.match('(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+)', curVerTimeStr)
					if datetime.datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), int(match.group(5)), int(match.group(6))) < tmpResList[0]:
						##begin add by laiyinfang 2014-04-16
						prResolveFromCodeInfoDict[bugid] = {}
						prResolveFromCodeInfoDict[bugid]['type'] = resList[1]
						prResolveFromCodeInfoDict[bugid]['reporter'] = self.getUserNameFromUid(resList[2], mysqlConn)
						prResolveFromCodeInfoDict[bugid]['status'] = resList[3]
						prResolveFromCodeInfoDict[bugid]['ownerinfo'] = self.getOwnerInfo(bugid, lastVerTimeStr, curVerTimeStr, mysqlConn, resList[8])
						prResolveFromCodeInfoDict[bugid]['function'] = self.getFunctionName(resList[4], mysqlConn)
						prResolveFromCodeInfoDict[bugid]['milestone'] = resList[5]
						prResolveFromCodeInfoDict[bugid]['desc'] = resList[6]
						prResolveFromCodeInfoDict[bugid]['commentcea'] = resList[7]
						prResolveFromCodeInfoDict[bugid]['localpath'] = ''
						prResolveFromCodeInfoDict[bugid]['impact'] =''
						prResolveFromCodeInfoDict[bugid]['menutree_iamge'] =''
						prResolveFromCodeInfoDict[bugid]['suggestion'] = ''
                                                #add by zhaoshie 20150612
						prResolveFromCodeInfoDict[bugid]['rootcause'] = ''
						prResolveFromCodeInfoDict[bugid]['rootcauseDetail'] = ''
						prResolveFromCodeInfoDict[bugid]['Solution'] = ''
						prResolveFromCodeInfoDict[bugid]['persoregen'] = 'Unknown'
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
                		impact,sugges,rootcause,rootcauseDetail,Solution = self.getImpactAndSuges(bugid, mysqlConn, lastVerTimeStr, curVerTimeStr)
                		prVeriSWOldResolveInfoDict[bugid]['impact'] = impact
                		prVeriSWOldResolveInfoDict[bugid]['menutree_iamge'] = ''
                		prVeriSWOldResolveInfoDict[bugid]['suggestion'] = sugges
                                #add by zhaoshie 20150612
				prVeriSWOldResolveInfoDict[bugid]['rootcause'] = rootcause
				prVeriSWOldResolveInfoDict[bugid]['rootcauseDetail'] = rootcauseDetail
				prVeriSWOldResolveInfoDict[bugid]['Solution'] = Solution
				prVeriSWOldResolveInfoDict[bugid]['persoregen'] = 'Unknown'
				self.needDeliverPR = True
			mysqlCursor.close()

	def deliverPRlist(self, conf, mysqlConn, prVeriSWFromCodeInfoDict, prVeriSWOldResolveInfoDict):
		##add and modified by renzhi.yang 15-1-13
		tempversion = conf.getConf('tempversion','the version is temp version or not<yes|no>','no')
		##if self.needDeliverPR and conf.getConf('delivresprweb', 'Deliver RESOLVED PR in Bugzilla <yes|no>', 'yes' if conf.getConf('isBigVersion', 'version is big version') == 'yes' and conf.getConf('sendto', 'email sendto<all|self>') == 'all' else 'no') == 'yes':
		if self.needDeliverPR and conf.getConf('delivresprweb', 'Deliver RESOLVED PR in Bugzilla <yes|no>', 'yes' if conf.getConf('isBigVersion', 'version is big version') == 'yes' and conf.getConf('sendto', 'email sendto<all|self>') == 'all' and tempversion == 'no' else 'no') == 'yes':
		##end by renzhi.yang
			prNeedDelivHash = {}
			for bugid,buginfo in prVeriSWFromCodeInfoDict.items():
				if buginfo['status'] in ['VERIFIED_SW', 'DELIVERED'] and self.ifDeliverCodeLoadPR(conf, mysqlConn, bugid):
					prNeedDelivHash[bugid] = [buginfo['status'], buginfo['milestone']]
					prVeriSWFromCodeInfoDict[bugid]['status'] = 'DELIVERED'
			for bugid,buginfo in prVeriSWOldResolveInfoDict.items():
				print "veri sw old resovle pr ------ %s" % bugid
				if buginfo['status'] in ['VERIFIED_SW', 'DELIVERED']:
					prNeedDelivHash[bugid] = [buginfo['status'], buginfo['milestone']]
					prVeriSWOldResolveInfoDict[bugid]['status'] = 'DELIVERED'
			mysqlConn.close()
			##test print 
			#for pr,infoList in prNeedDelivHash.items():
			#	print "deliver PR for test %d" % pr
			### test close here 
			self.deliverPR(conf, prNeedDelivHash)
		else:
			mysqlConn.close()

		curRow = 4

	def checkCodeLoadPR(self, version, base, tempdir, sendTo, info, mysqlConn, bugid):
		return True

	## check manual change PR, you must override this method
	def checkManualChangePR(self, conf, mysqlConn, bugid):
		tmpCursor = mysqlConn.cursor()
		tmpCursor.execute('SELECT bug_id,product_id,cf_branch FROM bugs WHERE bug_id=%d'%bugid)
		tmpList = tmpCursor.fetchone()
		version = conf.getConf('version', 'project current version')
		branch = conf.getConf('projbugbranch','bugzilla branch','TBD')
		branchArr = branch.split(',')
		if version[0:3] == conf.getConf('versionX','xls table versionX')[0:3] and tmpList[2] in branchArr:
			print "bug id------------------> %d"%tmpList[0]
			return True
		else :
			print "bug id------------------> %d"%tmpList[0]
			print "branch------------------> %s"%tmpList[2]
			return False

	## deliver code load PR
	def ifDeliverCodeLoadPR(self, conf, mysqlConn, bugid):
		tmpCursor = mysqlConn.cursor()
		tmpCursor.execute('SELECT bug_id,product_id,cf_branch FROM bugs WHERE bug_id=%d'%bugid)
		tmpList = tmpCursor.fetchone()
        	tmpCursor.close()
		version = conf.getConf('version', 'project current version')
		branch = conf.getConf('projbugbranch','bugzilla branch','TBD')
		branchArr = branch.split(',')
		if version[0:3] == conf.getConf('versionX','xls table versionX')[0:3] and tmpList[2] in branchArr:
			print "bug id------------------> %d"%tmpList[0]
			return True
		else :
			print "bug id------------------> %d"%tmpList[0]
			print "branch------------------> %s"%tmpList[2]
			return False

	## get bugzilla product id
	def getBugzillaProduct(self, conf):
		return re.findall('[^,]+', conf.getConf('bugzillaproductid', 'Product id in bugzilla'))

	### deliver PR status from browser user mechanize
	def deliverPR(self, conf, prHash):
		br = mechanize.Browser()
		br.set_handle_robots(False)
		br.set_handle_equiv(False)
		isLogedInBugzilla = False
		countPRNeedDeliver = 0
		curPRDeliverNumber = 1
		for pr,infoList in prHash.items():
			if infoList[0] in ['VERIFIED_SW', 'DELIVERED']:
				countPRNeedDeliver += 1
		print 'CAUTION: %d PRs are to be delivered or be added comment' % countPRNeedDeliver
		for pr,infoList in prHash.items():
			if infoList[0] in ['VERIFIED_SW', 'DELIVERED']:
				if not isLogedInBugzilla:
					while True:
						self.bugzillaloginname = conf.getConf('bugzillaloginname', 'Bugzilla loggin name', ask=2)
						self.bugzillapassword = conf.getConf('bugzillapassword', 'Bugzilla password', ask=2, echo=False)
						br.open('http://bugzilla.tcl-ta.com/index.cgi?GoAheadAndLogIn=1')
						br.select_form(name='login')
						br['Bugzilla_login'] = self.bugzillaloginname
						br['Bugzilla_password'] = self.bugzillapassword
						resp = br.submit()
						if re.search('Welcome\sto\sBugzilla!', resp.get_data()):
							print "Login bugzilla ok"
							break
						else:
							print "Login bugzilla fail, try again..."
					isLogedInBugzilla = True
				try:
					br.open('http://bugzilla.tcl-ta.com/show_bug.cgi?id=%s' % str(pr))
					print '%d) Deliver PR %s : %s' % (curPRDeliverNumber, str(pr), br.title())
					curPRDeliverNumber += 1
					response = br.response()
					#Python mechanize is broken, fixing it.
					response.set_data(response.get_data().replace("<br/>", "<br />")) 
					br.set_response(response)
					br.select_form(name='changeform')
					if infoList[0] == 'VERIFIED_SW':
						br['knob'] = ['deliver']
					version = conf.getConf('version','current version')
					verstr = 'SW%s' % version
					fullName = conf.getConf('bugzillaloginname', 'Bugzilla loggin name', 'hudson.admin')
					comment = 'The new ref is updated by %s with int tool superspam\n' % fullName
					if infoList[0] == 'VERIFIED_SW':
						comment += 'Change bug status to DELIVERED\n'						
					comment += 'New ref: %s' % verstr
					comment += '\nPlease use %s to verify' % verstr
					br['comment'] = comment
					if infoList[0] == 'VERIFIED_SW':
						milestone = infoList[1]
						if not re.search('\s%s\s' % verstr, milestone) and not re.search('\s%s$' % verstr, milestone):
							br['target_milestone'] = verstr
						#br['target_milestone'] = milestone
					br.submit()
				except:
					print 'WARNING: Deliver PR %s fail, please check' % str(pr)
					
			else:
				pass
				#self.sendUpdateNewRefToDeliveredPR(bugid, info, version, infoList[1])
		br.close()

	def getLoginName(self, mysqlConn, loginID):
		assigneeName = "None"
		curtmp = mysqlConn.cursor()
		curtmp.execute('SELECT login_name FROM profiles WHERE userid=%d' % loginID)
		assigneeName = curtmp.fetchone()[0]
		curtmp.close()
		return assigneeName
	def getImpactAndSuges(self, bugid, mysqlConn, lastVerTimeStr, curVerTimeStr):
		cursorTmp = mysqlConn.cursor()
		cursorTmp.execute("SELECT thetext from longdescs where bug_id = %s AND bug_when > '%s' and bug_when < '%s'" % (bugid,lastVerTimeStr,curVerTimeStr))
		impact = []
		sugges = []
                rootcause = []
                rootcauseDetail = []
                Solution = [] 
		while True:
			item  = cursorTmp.fetchone()
			if not item:
				break
			matches = re.search(r'###%%%Module_Impact:(.+?)###%%%Test_Suggestion:(.+?)###%%%Solution:(.+?)###%%%', item[0])
			if matches:
				if matches.group(1).strip() not in impact and matches.group(1).strip() != "":
					impact.append(matches.group(1).strip())
                		if matches.group(2).strip() not in sugges and matches.group(2).strip() != "":
					sugges.append(matches.group(2).strip())
                		if matches.group(3).strip() not in Solution and matches.group(3).strip() != "":
					Solution.append(matches.group(3).strip())

                        #add by zhaoshie 20150612
			matches = re.search(r'###%%%root cause:(.+?)###%%%root cause detail:(.+?)###%%%', item[0])
			if matches:
				if matches.group(1).strip() not in rootcause and matches.group(1).strip() != "":
					rootcause.append(matches.group(1).strip())
                		if matches.group(2).strip() not in rootcauseDetail and matches.group(2).strip() != "":
					rootcauseDetail.append(matches.group(2).strip())


		cursorTmp.close()	
       		return  '  ' if impact.__len__() == 0 else ','.join(impact), '  ' if sugges.__len__() == 0 else ','.join(sugges), '  ' if rootcause.__len__() == 0 else ','.join(rootcause), '  ' if rootcauseDetail.__len__() == 0 else ','.join(rootcauseDetail), '  ' if Solution.__len__() == 0 else ','.join(Solution)


	### get defect's type and status
	##  add by shie.zhao 2015-1-29
	def getDefectTypeStatus(self,mysqlConn,bugids):
                bugType = ''
		bugState = ''
		cur = mysqlConn.cursor()
		cur.execute('SELECT bug_id,bug_type,bug_status FROM bugs WHERE bug_id in (%s)' % str(bugids))	      
                #print cur
                bugtypestatus = {}
                while True:
                      resList = cur.fetchone()
                      if not resList:
			  break
		      bugid = resList[0]    
                      #print bugid           
                      if bugid in bugtypestatus.keys():
                          continue
                      #print resList[1],resList[2]
                      bugtypestatus[bugid] = {}
                      bugtypestatus[bugid]['type'] = resList[1]
                      bugtypestatus[bugid]['status'] = resList[2]
                cur.close()
                #print "get bug's Type and state"
		return bugtypestatus


	def getAllDeliveredBugs(self, mysqlConn, productIdNumList,allDeliveredBugsInfoDict,conf):
		## start modily by yangrenzhi 2015-02-5		
		productIdSqlList = []
		for oneProductIdNum in productIdNumList:
			productIdSqlList.append('product_id=%d' % oneProductIdNum)
			mysqlCurd = mysqlConn.cursor()
			sql = 'SELECT bug_id,bug_type,reporter,bug_status,function_id,target_milestone,short_desc,cf_comment_cea,assigned_to FROM bugs WHERE bug_status="DELIVERED" AND (%s)' % ' OR '.join(productIdSqlList)
			print sql
			mysqlCurd.execute(sql)
			while True:
				resList = mysqlCurd.fetchone()
				if not resList:
					break
				bugid = resList[0]
				if bugid in allDeliveredBugsInfoDict.keys():
					continue
				allDeliveredBugsInfoDict[bugid] = {}
				allDeliveredBugsInfoDict[bugid]['type'] = resList[1]
				allDeliveredBugsInfoDict[bugid]['reporter'] = self.getUserNameFromUid(resList[2], mysqlConn)
				allDeliveredBugsInfoDict[bugid]['status'] = resList[3]
				allDeliveredBugsInfoDict[bugid]['ownerinfo'] = self.getUserNameFromUid(resList[8],mysqlConn)
				allDeliveredBugsInfoDict[bugid]['function'] = self.getFunctionName(resList[4], mysqlConn)
				allDeliveredBugsInfoDict[bugid]['milestone'] = resList[5]
				allDeliveredBugsInfoDict[bugid]['desc'] = resList[6]
				allDeliveredBugsInfoDict[bugid]['commentcea'] = resList[7]
			mysqlCurd.close()
			##end add by laiyinfang 2014-04-16
