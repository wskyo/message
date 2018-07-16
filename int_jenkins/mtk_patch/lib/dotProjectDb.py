#!/usr/bin/python
############################################################################
## add by renzhi.yang for mkt patch create 2016-06-17
############################################################################
import MySQLdb
from time import strftime, localtime
import datetime
import time
import sys
import urllib
import urllib2
reload(sys)  
sys.setdefaultencoding('utf8')  
sys.path.append('/local/int_jenkins/lib')
from Integrity import IntegrityClient
import common


class dotProjectDb:
	def __init__(self):
		self.get_db_connection()
                #self.simplex=False
		
	def get_db_connection(self):
		try:
			common.show("%s Connect to prsm database" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
			self.db_conn = MySQLdb.connect(host="10.92.35.20", port=3306, user="INT_TOOLS", passwd="tcl@1234",db="dotproject",charset="utf8") #, charset="gbk"latin1
			self.db_cursor = self.db_conn.cursor()
			return self.db_cursor
		except Exception, e:
			print e
			sys.exit(1)

	def close_db(self):
		common.show("%s Close the connection of prsm database..." % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		if self.db_conn:
			common.show('Closed DB connecion.')
			self.db_conn.close()

	def query(self, sql, one_record=True):
		try:
			print "====sql====",sql
			self.db_cursor.execute(sql)
			if one_record:
 				result = self.db_cursor.fetchone()
 			else:
				result = self.db_cursor.fetchall()
			return result
		except Exception, e:
			common.show("Exception:%s\nWhile execute %s" % (e, sql), True)
			sys.exit(1)
	def changeListtoDict(self, listDetail):
		print "listDetail", listDetail
		projectIdDict = {}
		for item in listDetail:
			if item['projectId'] not in projectIdDict.keys():
				projectIdDict[item['projectId']] = item['importBranchName']
		return projectIdDict

	def getProjectIDlist(self, idlist):
		print "idlist",idlist
		projectIDList = []
		rmprojectList = []
		for item in idlist:
			projectIDList.append(item['projectId']) if item['projectId'] not in projectIDList else ''
		for item in idlist:
			for item1 in idlist:
				if item['importBranchName']==item1['importBranchName'] and item['projectId']!=item1['projectId']:
					if item['projectId']<item1['projectId'] and item1['projectId'] not in rmprojectList:
						rmprojectList.append(item1['projectId'])
		for rmp in rmprojectList:
			if rmp in projectIDList:
				projectIDList.remove(rmp)
		print "projectIDList",projectIDList
		return projectIDList
	
	def getProjectIDFromImportBranchSimplex(self, importBranchName):
		print "importBranchName",importBranchName
		projectList = []
		rmprojectList = []
		projectIDDict = {}
		GET_URL ="http://10.92.35.176/pms/project/mtkk-interface/0/getProjectIDFromImportBranch?importBranchName=%s" % importBranchName
		try:
			print GET_URL
			response = urllib2.urlopen(GET_URL)
			readline = response.read()
			print "getProjectIDFromImportBranchSimplex readline", readline
			readlineDict = eval(readline)
			projectList = self.getProjectIDlist(readlineDict['data'])
			return projectList
		except urllib2.HTTPError, e:
			print "Get projectid from simplex error !!" 
			print e

	def getProjectIDFromImportBranch(self, importBranchName):
		print "importBranchName",importBranchName
		#mysql = 'SELECT dotp_cts_branchs.project_id FROM dotp_projects,dotp_cts_branchs WHERE dotp_cts_branchs.import_name="%s" and dotp_projects.project_status=0' % importBranchName
		mysql = 'SELECT dotp_cts_branchs.project_id,dotp_cts_branchs.branch_name FROM dotp_projects,dotp_cts_branchs WHERE dotp_cts_branchs.project_id =dotp_projects.project_id AND dotp_cts_branchs.import_name="%s" and dotp_projects.project_status=0 and dotp_cts_branchs.branch_flag=0' % importBranchName 
		projectList = []
		rmprojectList = []
		projectIDDict = {}
		try:
			result = self.query(mysql, False)
			if result:
				for item in result:
					projectIDDict[item[0]]=item[1]
				print "projectIDDict ",projectIDDict
			else:
				print "the projectid should be existing in db"
				#sys.exit(1)

			projectList=projectIDDict.keys()
			for k1 in projectIDDict.keys():
				for k2 in projectIDDict.keys():
					if k1!=k2 and projectIDDict[k1]==projectIDDict[k2]:
						if k1<k2:
							if k2 in rmprojectList:
								continue
							else:
								rmprojectList.append(k2) 
			
			for rmp in rmprojectList:
				if rmp in projectList:
					projectList.remove(rmp)  
                 
			return projectList

		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)

	def getAllProjectIDFromImportBranchFromSimplex(self, importBranchName):
		print "importBranchName",importBranchName
		projectList = []
		GET_URL ="http://10.92.35.176/pms/project/mtkk-interface/0/getAllProjectIDFromImportBranch?importBranchName=%s" % importBranchName
		try:
			print GET_URL
			response = urllib2.urlopen(GET_URL)
			readline = response.read() 
			print "readline", readline
			readlineDict = eval(readline)
			print "getAllProjectIDFromImportBranchFromSimplex readlineDict",readlineDict
			projectList = self.getProjectIDlist(readlineDict['data'])
			return projectList
		except urllib2.HTTPError, e:  
			print "Get projectid from simplex error !!" 
			print e
	def getAllProjectIDFromImportBranch(self, importBranchName):
		print "importBranchName",importBranchName
		#mysql = 'SELECT dotp_cts_branchs.project_id FROM dotp_projects,dotp_cts_branchs WHERE dotp_cts_branchs.import_name="%s" and dotp_projects.project_status=0' % importBranchName
		mysql = 'SELECT dotp_cts_branchs.project_id,dotp_cts_branchs.branch_name FROM dotp_projects,dotp_cts_branchs WHERE dotp_cts_branchs.project_id =dotp_projects.project_id AND dotp_cts_branchs.import_name="%s" and dotp_projects.project_status=0' % importBranchName 
		projectList = []
		try:
			result = self.query(mysql, False)
			if result:
				for item in result:
					projectid = item[0]
					print "projectid ",projectid
					projectList.append(projectid) if projectid not in projectList  else ''
				return projectList
			else:
				print "the projectid should be existing in db"
				sys.exit(1)			                   
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)


	def getDevBranchNameFromIProjectID(self, projectIDList, projectid_devBranch_dict,importbranch):
		print "projectIDList",projectIDList
		branchList = []
		for projectID in projectIDList:
			if projectID not in projectid_devBranch_dict.keys():
				projectid_devBranch_dict[projectID] = []
			mysql = 'SELECT branch_name FROM dotp_cts_branchs WHERE  project_id=%s and branch_flag=0 and import_name="%s"' % (projectID,importbranch)
			try:
				result = self.query(mysql, False)
				if result:
					for item in result:			
						devbranchName = item[0]
						print "devbranchNameList ",devbranchName
						branchList.append(devbranchName) if devbranchName not in branchList else ''
						projectid_devBranch_dict[projectID].append(devbranchName) if devbranchName not in projectid_devBranch_dict[projectID] else ''		
					
				else:
					print "the development code branch List should be existing in db"
					#sys.exit(1)			
			except Exception, e:
				print e
				print "connect to prsm failed"
				sys.exit(1)
		return branchList

	def getDevBranchNameFromIProjectIDSimplex(self, projectIDList, projectid_devBranch_dict):
		print "projectIDList in simplex", projectIDList
		branchList = []
		for projectID in projectIDList:
			if projectID not in projectid_devBranch_dict.keys():
				projectid_devBranch_dict[projectID] = []
			GET_URL ="http://10.92.35.176/pms/project/mtkk-interface/0/getDevBranchNameFromIProjectID?projectId=%s" % projectID
			try:
				print 'GET_URL:getDevBranchNameFromIProjectID',GET_URL
				response = urllib2.urlopen(GET_URL)
				readline = response.read()
				readlineDict = eval(readline)
				print "getDevBranchNameFromIProjectIDSimplex readlineDict", readlineDict
				for item in readlineDict["data"]:
					branchList.append(item) if item not in branchList else ''
					projectid_devBranch_dict[projectID].append(item) if item not in projectid_devBranch_dict[projectID] else ''
			except urllib2.HTTPError, e:  
				print "Get dev branch list from simplex error !!" 
				print e
		return branchList
	def getContactIDList(self, projectIDList):
		print "projectIDList",projectIDList
		ContactIDList = []
		for projectid in projectIDList:
			mysql = 'SELECT project_owner FROM dotp_projects WHERE  project_id=%s' % projectid
			GET_URL ="http://10.92.35.176/pms/project/mtkk-interface/0/getContactIDList?projectId=%s" % projectid
			if self.simplex:
				try:
					print GET_URL
					response = urllib2.urlopen(GET_URL)
					readline = response.read()
					readlineDict = eval(readline)
					print "getContactIDList readline", readline
					ContactID = readlineDict["data"]
					ContactIDList.append(ContactID)	 if ContactID not in ContactIDList else ''
				except urllib2.HTTPError, e:
					print "Get dev branch list from simplex error !!" 
			else:
				try:
					result = self.query(mysql, True)
					if result:			
						ContactID = result[0]
						print "ContactID ",ContactID
						ContactIDList.append(ContactID)	 if ContactID not in ContactIDList else ''				
					else:
						print "the ContactID should be existing in db"
						sys.exit(1)			
				except Exception, e:
					print e
					print "connect to prsm failed"
					sys.exit(1)
		return ContactIDList
	def getSpmEmailList(self, ContactIDList):
		print "ContactIDList",ContactIDList
		spmEmailList = []
		for contactID in ContactIDList:
			GET_URL ="http://10.92.35.176/pms/project/mtkk-interface/0/getSpmEmailList?userId=%s" % contactID
			mysql = 'SELECT dotp_contacts.contact_email FROM dotp_users, dotp_contacts WHERE dotp_users.user_contact = dotp_contacts.contact_id AND dotp_users.user_id =%s' % contactID
			if self.simplex:
				try:
					print "GET_URL",GET_URL
					response = urllib2.urlopen(GET_URL)
					readline = response.read()
					readlineDict = eval(readline)
					print "readline getSpmEmailList", readline
					spmEmail = readlineDict["data"]
					spmEmailList.append(spmEmail) if spmEmail not in spmEmailList else ''
				except urllib2.HTTPError, e:  
					print "Get dev branch list from simplex error !!" 
			else:
				try:
					result = self.query(mysql, True)
					if result:		
						spmemail = result[0]
						print "spmemail ",spmemail
						spmEmailList.append(spmemail) if spmemail not in spmEmailList else ''				
					else:
						print "the ContactID should be existing in db"
						sys.exit(1)			
				except Exception, e:
					print e
					print "connect to prsm failed"
					sys.exit(1)
		return spmEmailList
	def insertImportInfoToSimplex(self,project_id,import_patch,vnum,pnum,patch_type,eservice_ID,comment,mtkpatchtype):
		if not comment:
			comment = 'N/A'
		comment = comment.decode('utf-8')
		if len(comment) > 255:
			comment = comment[:254]
		#begin insert to simplex
		paraDict = {}
		paraDict['projectId'] = project_id
		paraDict['importPatch'] = import_patch
		paraDict['vnum'] = vnum
		paraDict['pnum'] = pnum
		paraDict['patchType'] = patch_type
		paraDict['eserviceId'] = eservice_ID
		paraDict['comment'] = comment
		paraDict['mtkPatchType'] = mtkpatchtype
		GET_URL ="http://10.92.35.176/pms/project/mtkk-interface/0/insertImportInfo"
		try:
			print "insertImportInfoToSimplex GET_URL",GET_URL
			response = urllib2.urlopen(GET_URL,urllib.urlencode(paraDict))
			readline = response.read() 
			print "insertImportInfoToSimplex readline", readline
		except urllib2.HTTPError, e:  
			print "insertImportInfo to simplex error !!"
			print e
	def insertImportInfo(self,project_id,import_patch,vnum,pnum,patch_type,eservice_ID,comment,mtkpatchtype,mtkdefectid):
		if not comment:
			comment = 'N/A'
		comment = comment.decode('utf-8')
		if len(comment) > 255:
			comment = comment[:254]
		insertsql = "INSERT INTO dotp_mtk_import  (project_id,import_patch,vnum,pnum,patch_type,eservice_ID,comment,mtk_patch_type,mtk_defect) \
		   VALUES(%s,'%s','%s','%s','%s','%s','%s','%s','%s') " \
%(project_id,import_patch,vnum,pnum,patch_type,eservice_ID,comment,mtkpatchtype,mtkdefectid)
		try:
			print insertsql
		except Exception, e:
			print e
			print "There is error print info"
		try:			
			self.db_cursor.execute(insertsql)
			self.db_conn.commit()
		
		except Exception, e:
			print e
			if e[0] == 1062:
				print "Duplicate entry"
			else:
				print "insert error!!!"
				sys.exit(0)
	def insertImportCommitIDInfoToSimplex(self,import_id,commit_id,import_patch_link,git_name):
		GET_URL ="http://10.92.35.176/pms/project/mtkk-interface/0/insertImportCommitIDInfo?importId=%s&commitId=%s&importPatchLink=%s&gitName=%s" %(import_id,commit_id,import_patch_link,git_name)
		try:
			print GET_URL
			response = urllib2.urlopen(GET_URL)
			readline = response.read() 
			print "insertImportCommitIDInfo readline", readline
		except urllib2.HTTPError, e:  
			print "insertImportCommitIDInfo to simplex error !!"   
			print e   


	def insertImportCommitIDInfo(self,import_id,commit_id,import_patch_link,git_name):
		insertsql = "INSERT INTO dotp_mtk_commit (import_id,commit_id,import_patch_link,git_name) \
		   VALUES(%s,'%s','%s','%s') " \
%(import_id,commit_id,import_patch_link,git_name)
		print insertsql
		try:			
			self.db_cursor.execute(insertsql)
			self.db_conn.commit()		
		except Exception, e:
			print e
			if e[0] == 1062:
				print "Duplicate entry"
			else:
				print "insert error!!!"
    				sys.exit(0)


	def getImportIDAfterInsertSimplex(self,eachProjectID,importBranchName,vnum,pnum,patch_type,eservice_ID):
		GET_URL ="http://10.92.35.176/pms/project/mtkk-interface/0/getImportIDAfterInsert?projectId=%s&importPatch=%s&vnum=%s&pnum=%s&patchType=%s&eserviceId=%s" %(eachProjectID,importBranchName,vnum,pnum,patch_type,eservice_ID)
		try:
			print "getImportIDAfterInsertSimplex,GET_URL",GET_URL
			response = urllib2.urlopen(GET_URL)
			readline = response.read()
			print "getImportIDAfterInsertSimplex readline", readline
			readlineDict = eval(readline)
			print readlineDict['data']
			import_id = readlineDict['data']['autoId']
		except urllib2.HTTPError, e:  
			print "get impoet id from simplex error !!" 
			print e
		return import_id
	def getImportIDAfterInsert(self,eachProjectID,importBranchName,vnum,pnum,patch_type,eservice_ID):
		mysql = 'SELECT id FROM dotp_mtk_import WHERE  project_id=%s and import_patch="%s" and vnum="%s" and pnum="%s" and patch_type="%s" and eservice_ID="%s"' % (eachProjectID,importBranchName,vnum,pnum,patch_type,eservice_ID)
		print "mysql",mysql
		print eachProjectID,importBranchName,vnum,pnum,patch_type,eservice_ID
		try:
			result = self.query(mysql, True)
			print "result",result
			if result:							
				import_id = result[0]
				print "import_id ",import_id						
			else:
				print "the import_id should be existing in db"
				sys.exit(1)			
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)
		return import_id

	def insertAllImportInfoTO_importSheet(self,devCodeProjectIDList,importBranchName,patch_type,vnum,pnum,eservice_ID,comment,mtkpatchtype):
		import_id = ''
		mtkdefect_id = ''
		mtkdefect_id = self.getMtkdefectID_from_eserviceid(eservice_ID)
		print "devCodeProjectIDList,importBranchName,patch_type,vnum,pnum,eservice_ID,comment,mtkpatchtype,tmkdefectid",devCodeProjectIDList,importBranchName,patch_type,vnum,pnum,eservice_ID,comment,mtkpatchtype,mtkdefect_id
		if self.insertDataToPrsm:
			for eachProjectID in devCodeProjectIDList:
				self.insertImportInfo(eachProjectID,importBranchName,vnum,pnum,patch_type,eservice_ID,comment,mtkpatchtype,mtkdefect_id)
		#for simplex data start
			devCodeAllProjectIDListSimplex = self.getAllProjectIDFromImportBranchFromSimplex(importBranchName)
		for oneProjectID in devCodeAllProjectIDListSimplex:
			self.insertImportInfoToSimplex(oneProjectID,importBranchName,vnum,pnum,patch_type,eservice_ID,comment,mtkpatchtype)
		#for simplex data end

	def insertImportCommitInfoTO_dotp_mtk_commit(self,importIdDict,devCodeProjectIDList,importBranchName,patch_type,vnum,pnum,eservice_ID,commit_id,import_patch_link,git_name):
		for eachProjectID in devCodeProjectIDList:			
			import_id = self.getImportIDAfterInsert(eachProjectID,importBranchName,vnum,pnum,patch_type,eservice_ID)
			print "the import id is %s" % import_id
			if eachProjectID not in importIdDict[patch_type].keys():
				importIdDict[patch_type][eachProjectID] = import_id 
			self.insertImportCommitIDInfo(import_id,commit_id,import_patch_link,git_name)
		return importIdDict

	def insertImportCommitInfoTO_simplex_mtk_commit(self,importIdDict,devCodeProjectIDList,importBranchName,patch_type,vnum,pnum,eservice_ID,commit_id,import_patch_link,git_name):
		for eachProjectID in devCodeProjectIDList:			
			import_id = self.getImportIDAfterInsertSimplex(eachProjectID,importBranchName,vnum,pnum,patch_type,eservice_ID)
			print "the import id in simplex is %s" % import_id
			if eachProjectID not in importIdDict[patch_type].keys():
				importIdDict[patch_type][eachProjectID] = import_id 
			self.insertImportCommitIDInfoToSimplex(import_id,commit_id,import_patch_link,git_name)
		return importIdDict

	def insertImportId_And_DevBranch_To_dotp_mtk_merge_simplex(self,ImportID, DevBranch,owner):
		for eachBranch in DevBranch:
			#begin insert to simplex
			#if self.simplex:
			GET_URL ="http://10.92.35.176/pms/project/mtkk-interface/0/insertImportId_And_DevBranch_To_dotp_mtk_merge?importId=%s&mergePatch=%s&owner=%s" %(ImportID,eachBranch,owner) 
			try:
				print GET_URL
				response = urllib2.urlopen(GET_URL)
				readline = response.read() 
				print "insertImportId_And_DevBranch_To_dotp_mtk_merge readline", readline
			except urllib2.HTTPError, e:  
				print "insertImportCommitIDInfo to simplex error !!" 
				print e
              
 	def insertImportId_And_DevBranch_To_dotp_mtk_merge(self,ImportID, DevBranch,owner):   
 		for eachBranch in DevBranch:                 	
			insertsql = "INSERT INTO dotp_mtk_merge (import_id,merge_patch,owner) \
		   VALUES(%s,'%s','%s') " \
%(ImportID,eachBranch,owner)
			print insertsql
			try:			
				self.db_cursor.execute(insertsql)
				self.db_conn.commit()		
			except Exception, e:
				print e
				if e[0] == 1062:
					print "Duplicate entry"
				else:
					print "insert error!!!"
    					sys.exit(0)

	def getMtkdefectID_from_eserviceid(self,eservice_ID):
		mtk_defect_id = ''
		url = "https://alm.tclcom.com:7003/webservices/10/2/Integrity/?wsdl"
		try:
			db_conn = IntegrityClient(url, credential_username='hz.int', credential_password='ptc')
			item_type = 'MTK Defect'
			mysqlCursor = db_conn.getItemsByCustomQuery(fields=['ID'], query="((field[Type] = %s) and (field[MTK Issue ID] contains %s))" % (item_type,eservice_ID))
			if len(mysqlCursor)>0 and mysqlCursor[0]:
				print 'MTK Defect ID', mysqlCursor[0]['ID'][1].value
				mtk_defect_id = mysqlCursor[0]['ID'][1].value
		except Exception, e:
			print e			
		return mtk_defect_id




		



