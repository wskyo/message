#!/usr/bin/python
import os
import sys
import re
from commands import *
import time
import datetime
import MySQLdb
import glob
sys.path.append('/local/int_jenkins/lib')
from Utils import *
from Config import *
import common
import send_mail
from time import strftime, localtime
import commands
import tempfile

class CreateTask:
	def __init__(self):
		self.get_db_connection()

	def get_db_connection(self):
		try:
			print "%s Connect to prsm database" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			self.db_conn = MySQLdb.connect(host="10.92.35.20", port=3306, user="INT_TOOLS", passwd="tcl@1234",db="dotproject",charset="utf8") #, charset="gbk"latin1
			self.db_cursor = self.db_conn.cursor()
			return self.db_cursor
		except Exception, e:
			print e
			sys.exit(1)


	def close_db(self):
		print "%s Close the connection of prsm database..." % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		if self.db_conn:
			print 'Closed DB connecion.'
			self.db_conn.close()


	def query(self, sql, one_record=True):
		try:
			self.db_cursor.execute(sql)
			if one_record:
 				result = self.db_cursor.fetchone()
 			else:
				result = self.db_cursor.fetchall()
			return result
		except Exception, e:
			print "Exception:%s\nWhile execute %s" % (e, sql)
			sys.exit(1)


	def getUserTeamFromUsername(self, username,useremail):
		#teamDict = {1:'App1',2:'System',3:'App2',4:'Driver',5:'perso',6:'INT',7:'tools',8:'SPM',9:'Tel',10:'Other',11:'BSP',12:'App3',13:'ODM'}
		print "username",username
		mysql = 'SELECT user_team FROM dotp_users WHERE user_username="%s" or user_username="%s"' % (username,useremail)
		try:
			result = self.query(mysql, True)
			if result:				
				userteamid = result[0]
				print "userteamid ",userteamid				
				return userteamid
			else:
				print "the userteamid should be existing in db"
				sys.exit(1)
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)
        def getTeamGroup(self):
        	TeamDict = {}
                mysql = "select sysval_value  FROM dotp_sysvals where sysval_title ='UserTeam' "
		try:
			result = self.query(mysql, True)
			print result			
			if result:				
				strTeam = result[0]
				teamList = strTeam.split('\n')
				for value in teamList:
					if value.strip() == '' or value.strip() == None:
						continue
					tmpList = value.split('|')
					if (tmpList[0] != None and tmpList[1] != None):
						if tmpList[0] not in TeamDict.keys():
							TeamDict[tmpList[0].strip()] = tmpList[1].strip()
			print TeamDict
			return TeamDict
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)
        
	def getUserTeamleader(self, userteamid):
		mysql = 'SELECT user_id,user_contact,user_username FROM dotp_users WHERE user_team="%s" and user_type=4' % userteamid
		try:
			result = self.query(mysql, True)
			print result			
			if result:				
				userteamleaderid = result[0]
				usercontactid = result[1]
				userteamname = result[2]
				print "userteamleaderid ",userteamleaderid
				print "usercontactid ",usercontactid	
				print "userteamname ",userteamname				
				return userteamleaderid,usercontactid,userteamname
			else:
				print "the userteamid should be existing in db"
				sys.exit(1)
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)

	def getUserTeamleaderemail(self, usercontactid):
		mysql = 'SELECT contact_email FROM dotp_contacts WHERE contact_id="%s"' % usercontactid
		try:
			result = self.query(mysql, True)
			print result			
			if result:
				userteamemail = result[0]
				print "userteamemail ",userteamemail				
				return userteamemail
			else:
				print "the usercontactid should be existing in db"
				sys.exit(1)
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)

	def getProjectID(self, projectname):
		mysql = 'SELECT project_id FROM dotp_projects WHERE project_name="%s"' % projectname
		try:
			result = self.query(mysql, True)
			print result			
			if result:
				ProjectID = result[0]
				print "ProjectID ",ProjectID				
				return ProjectID
			else:
				print "the ProjectID should be existing in db"
				sys.exit(1)
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)


	def getParentID(self, projectid, task_name, task_desc):
		mysql = 'SELECT id FROM dotp_tasks_item WHERE task_project_id="%s" and task_type="ISDM" and task_name="%s" and task_desc="%s"' % (projectid,task_name,task_desc)
		try:
			result = self.query(mysql, True)
			print result			
			if result:
				ParentID = result[0]
				print "ParentID ",ParentID				
				return ParentID
			else:
				print "the ParentID should be existing in db"
				#sys.exit(1)
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)
	def getSonID(self, parentid, task_desc):
		#task_project_id,task_priority,task_type,task_name,task_status,task_desc
		mysql = 'SELECT id FROM dotp_tasks_detail WHERE  parentId="%s" and task_desc="%s"' % (parentid,task_desc)
		try:
			result = self.query(mysql, True)
			print result			
			if result:
				SonID = result[0]
				print "SonID ",SonID				
				return SonID
			else:
				print "the ParentID should be existing in db"
				#sys.exit(1)
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)

	def CreateFatherTask(self,projectname,updatedSdmDict, sdm_author_dict,projectid,version):
		taskinfo = {}
		task_project_id = projectid
		task_priority = 'P1(Quick)'
		task_type = 'ISDM'
		task_status = 'ongoing'
		task_start_date = datetime.datetime.now()
		task_planned_date = task_start_date + datetime.timedelta(days =1)
		task_planned_date  = task_planned_date.strftime('%Y-%m-%d %H:%M:%S')
		fatger_assigner = []
		fatger_assigner_str = ''
		fatger_assigner_name_str = ''
		print "sdm_author_dict.keys()",sdm_author_dict.keys()
		i = 1			
		for item in sdm_author_dict.keys():			
			task_name = '[%s]SDM Value Change Check' % version
			n = 1
			taskinfo[i] = {}
			taskinfo[i]['sontaskInfo'] = {}
			task_desc_detal = ''
			for eachsdm in sdm_author_dict[item]['sdminfor']:
				task_desc_detal += str(n) +") " + eachsdm + '<br>'
				n = n + 1
				if n > len(sdm_author_dict[item]['sdminfor']):
					break
			task_desc = "SDM value changed:" +'<br>'+ task_desc_detal
			print 'task_desc',task_desc
			task_owner = sdm_author_dict[item]['userteamleaderid']
			task_owner_name = sdm_author_dict[item]['teamleaderusername']
			task_assigned = sdm_author_dict[item]['userteamleaderid']
			if self.getParentID(projectid, task_name, task_desc):
				break
			insertsql = "INSERT INTO dotp_tasks_item  (task_project_id,task_priority,task_type,task_name,task_status,task_desc,task_owner,task_assigned,task_start_date,task_planned_date) \
		   VALUES(%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s') " \
%(task_project_id,task_priority,task_type,task_name,task_status,task_desc,task_owner,task_assigned,task_start_date,task_planned_date)
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
			parentId = self.getParentID(projectid, task_name, task_desc)
			fatger_assigner, taskinfo[i]['sontaskInfo'] = self.CreateSonTask(updatedSdmDict,sdm_author_dict[item]['sdminfor'],task_owner,parentId,sdm_author_dict[item]['teamleaderusername'])
			print 'fatger_assigner',fatger_assigner			
			if len(fatger_assigner) > 1:
				fatger_assigner_str = ','.join(fatger_assigner)
				self.updateFatherTaskAssiner(parentId,fatger_assigner_str)
			print "i",i
			taskinfo[i]['projectname'] = projectname
			taskinfo[i]['task_priority'] = task_priority
			taskinfo[i]['task_type'] = task_type
			taskinfo[i]['task_status'] = task_status
			taskinfo[i]['task_name'] = task_name
			taskinfo[i]['task_desc'] = task_desc
			taskinfo[i]['task_owner'] = task_owner_name
			taskinfo[i]['task_assigned'] = task_owner_name
			taskinfo[i]['task_planned_date'] = task_planned_date
			i = i + 1	
		print "taskinfo",taskinfo	
		return taskinfo

	def CreateSonTask(self,updatedSdmDict,sdm_list,task_owner,parentId,assigner):
		print "parentId" ,parentId
		task_owner = task_owner
		task_assigned = task_owner
		task_status = 'ongoing'
		task_start_date = datetime.datetime.now()
		task_planned_date = task_start_date + datetime.timedelta(days =1)
		task_planned_date = task_planned_date.strftime('%Y-%m-%d %H:%M:%S')
		task_block = None
		fatger_assigner = []
		sonTaskInfo = {}
		#fatger_assigner_str = ''
		for item in sdm_list:
			print 'item',item
			print 'updatedSdmDict[item]',updatedSdmDict[item]['comment']
			print "updatedSdmDict[item]['pr']",updatedSdmDict[item]['pr']	
			print "updatedSdmDict[item]['author']",updatedSdmDict[item]['author']			
			task_desc = "SDM:" +item +'<br>'+updatedSdmDict[item]['comment']+'<br>'+'Related PR: '+ ','.join(updatedSdmDict[item]['pr']) + '<br>'+'Modified by:' + updatedSdmDict[item]['author']
			print 'task_desc',task_desc
			if item not in sonTaskInfo.keys():
				sonTaskInfo[item] = {}
			sonTaskInfo[item]['task_status'] = task_status
			sonTaskInfo[item]['task_assigned'] = assigner
			sonTaskInfo[item]['task_desc'] = task_desc
			sonTaskInfo[item]['task_start_date'] = task_start_date
			sonTaskInfo[item]['task_planned_date'] = task_planned_date
			sonTaskInfo[item]['task_owner'] = assigner
			sonTaskInfo[item]['pr'] = updatedSdmDict[item]['pr']
			sonTaskInfo[item]['patch_link'] = updatedSdmDict[item]['url'][0]
			insertsql = "INSERT INTO dotp_tasks_detail  (task_desc,task_owner,task_assigned,task_status,task_start_date,task_planned_date,parentId,task_block) \
		   VALUES('%s','%s','%s','%s','%s','%s','%s','%s') " \
%(task_desc,task_owner,task_assigned,task_status,task_start_date,task_planned_date,parentId,task_block)
			print insertsql
			try:			
				self.db_cursor.execute(insertsql)
				self.db_conn.commit()
				fatger_assigner.append(str(task_assigned))
		
			except Exception, e:
				print e
				if e[0] == 1062:
					print "Duplicate entry"
				else:
					print "insert error!!!"
    					sys.exit(0)
			SonID = self.getSonID(parentId, task_desc)
			link =  "http://10.92.35.20/SmartTask/?m=tasks&a=edittask&task_id=%s" % SonID
			sonTaskInfo[item]['link'] = link
		return fatger_assigner,sonTaskInfo



	def updateFatherTaskAssiner(self,parentId,fatger_assigner_str):
		print 'parentId,fatger_assigner_str',parentId,fatger_assigner_str
		updatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		updatesql = 'UPDATE dotp_tasks_item SET `task_assigned` = "%s",`updatetime` = "%s" WHERE id = %s '%(fatger_assigner_str,updatetime,parentId)
		print updatesql
		try:			
			self.db_cursor.execute(updatesql)
			self.db_conn.commit()		
		except Exception, e:
			print e


	def getProjectName(self, codeBranchName):
		print "codeBranchName",codeBranchName
		mysql = 'SELECT dotp_projects.project_name FROM dotp_projects,dotp_cts_branchs WHERE dotp_projects.project_id = dotp_cts_branchs.project_id AND branch_flag=0 AND branch_name = "%s"' % codeBranchName
		try:
			result = self.query(mysql, True)
			if result:				
				projectname = result[0]
				print "projectname ",projectname				
				return projectname
			else:
				print "the projectname should be existing in db"
				sys.exit(1)
		except Exception, e:
			print e
			print "connect to WR failed"
			sys.exit(1)
			

class Email:
	def mail_head_content(self, project,version,taskinfo):
		html = '''<html xmlns="http://www.w3.org/1999/xhtml">
		<head>
		<meta http-equiv="Content-Type" content="text/html;charset=gb2312"/>
		<style type="text/css">
		body {font-family:arial; font-size:10pt;}
		td {font-family:arial; font-size:10pt;}
		</style>
		<title>SDM changed value</title>
		</head>
		<body>
		<p>Dear team leaders,</p>
		<p> </p>
		'''
		html += '<p align=\'Left\'>Some SDM value updated in %s of %s ,Please check the tasks in SmartTask,thanks!</b><br/></p>'%(project, version)
		html += '<p align=\'Left\'>Link in SmartTask:<a href=http://10.92.35.20/SmartTask/?m=tasks>http://10.92.35.20/SmartTask/?m=tasks</a></b><br/></p>'
		html += '<p align=\'Left\'>Task information from SmartTask:</b><br/></p>'   

		strFormat_title = '<tr><th bgcolor="#99cc66" align="left" width="3%">NO</th><th bgcolor="#99cc66" align="center" width="15%">TaskName</th><th bgcolor="#99cc66" align="left" width="8%">Assigner</th><th bgcolor="#99cc66" align="center" width="5%">Status</th><th bgcolor="#99cc66" align="center" width="15%">Deadline</th><th bgcolor="#99cc66" align="center" width="32%">Description</th><th bgcolor="#99cc66" align="center" width="8%">Related Patch Link</th></tr>'
		strFormat = '<tr bgcolor="#ffece6" ><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td></tr>'

		strFormat_forsontask = '<tr><td align="left" colspan="2">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left">%s</td><td align="left"><a href=%s>%s</a></td></tr>'
		html += '<table border="1" width="125%" cellpadding="2" cellspacing="0">'
		html +=  strFormat_title	
		i = 1
		for key in taskinfo.keys():			
			html += strFormat %(i,taskinfo[key]['task_name'],taskinfo[key]['task_assigned'],taskinfo[key]['task_status'],taskinfo[key]['task_planned_date'],taskinfo[key]['task_desc'],'')
			for item in taskinfo[key]['sontaskInfo'].keys():
				#html += strFormat %('','','','','',taskinfo[key]['sontaskInfo'][item]['task_owner'],taskinfo[key]['sontaskInfo'][item]['task_assigned'],taskinfo[key]['sontaskInfo'][item]['task_status'],taskinfo[key]['sontaskInfo'][item]['task_planned_date'],taskinfo[key]['sontaskInfo'][item]['task_desc'])				
				html += strFormat_forsontask %('',taskinfo[key]['sontaskInfo'][item]['task_assigned'],taskinfo[key]['sontaskInfo'][item]['task_status'],taskinfo[key]['sontaskInfo'][item]['task_planned_date'],taskinfo[key]['sontaskInfo'][item]['task_desc'],taskinfo[key]['sontaskInfo'][item]['patch_link'],taskinfo[key]['sontaskInfo'][item]['patch_link'])
			i += 1
		html += '</table>'
		html = html.encode('utf-8')
		return html

	def mail_bottom_content(self):
		html = '<br/><img src="cid:ReleaseMailLogo.jpg">'
		html += '<p><font color="gray">'
		html += 'Best Regards,<br />'
		html += 'hudson.admin.hz<br />'
		html += 'TEL:  0752-8228580 <br />'
		html += 'MAIL: hudson.admin.hz@tcl.com<br />'
		html += 'ADDR: HZ Product Innovation Center SWD1 TCL COMMUNICATION TECHNOLOGY HOLDINGS LIMITED'+ \
            '17 Huifeng 4th,ZhongKai Hi-tech Development District,Huizhou,Guangdong 516006 P.R.China'
		html += '</font></p>'
		html += '</body>'
		html += '</html>'
		html = html.encode('utf-8')
		return html

	def createEmail(self, patchownerList, emailToList, project, version,taskinfo):
		to_list = emailToList
		cc_list_confirm = ['shie.zhao@tcl.com','yunqing.huang@tcl.com','yuanpeng.liu@tcl.com','zongmin.lu@tcl.com','xinyao.ye.hz@tcl.com','guangming.yang.hz@tcl.com']
		cc_list = patchownerList + cc_list_confirm	
		print "to_list",to_list
		print "cc_list",cc_list
		subject = "[SDM Check][%s][v%s] Please check the related tasks about SDM changed value" %(project,version)	
		mail_content = self.mail_head_content(project, version,taskinfo)
		mail_content += self.mail_bottom_content()
		common.show("Send mail")
		tmp_dir = tempfile.mktemp('mail', 'tmp')
		os.makedirs(tmp_dir)
		(img_dir, attach_dir) = self.prepare_attach(tmp_dir)
		send_mail.send_mail('hudson.admin.hz', 'hudson.admin.hz@tcl.com', subject, mail_content, to_list,'hudson.admin.hz','Hzsw#123',cc_list, img_dir, attach_dir)

	def prepare_attach(self,tmp_dir):
		img_dir = '%s/image' % tmp_dir
		attach_dir = '%s/attach' % tmp_dir
		common.docmd('mkdir %s' % img_dir)
		common.docmd('mkdir %s' % attach_dir)
		tools_int_dir =  '/local/int_jenkins/misc'
		common.docmd('cp %s/SuperSpamReleaseMailFootLogoOneTouch.jpg %s/ReleaseMailLogo.jpg' % (tools_int_dir, img_dir))
		return (img_dir, attach_dir)


def main():

	db = CreateTask()
	print "begin create task in prsm"	
	updatedSdmDict = sys.argv[1]
	codeBranchName = sys.argv[2]
	projectname = db.getProjectName(codeBranchName)
	print "updatedSdmDict",updatedSdmDict
	version = sys.argv[3]
	print type(updatedSdmDict)
	updatedSdmDict = eval(updatedSdmDict)
	print type(updatedSdmDict)
	sdm_author_dict = {}
	emailToList = []
	patchownerList = []
	taskinfo = {}

	for item in dict(updatedSdmDict).keys():
		author = updatedSdmDict[item]['author'].split(' ')[0]
		print "author",	author
		authorEmail = updatedSdmDict[item]['author'].split(' ')[1].strip('<').strip('>').split('@')[0]
		email_str = updatedSdmDict[item]['author'].split(' ')[1].strip('<').strip('>').strip()
		if email_str and (email_str not in patchownerList):
			patchownerList.append(email_str)
		print "authorEmail",authorEmail
		userteamid = db.getUserTeamFromUsername(author,authorEmail)
		print "userteamid",userteamid
		userteamleaderid,usercontactid,userteamleadername = db.getUserTeamleader(userteamid)
		print "userteamleaderid,usercontactid,userteamleadername",userteamleaderid,usercontactid,userteamleadername
		userteamleaderemail = db.getUserTeamleaderemail(usercontactid)
		if userteamleaderemail and (userteamleaderemail not in emailToList):
			emailToList.append(userteamleaderemail)
		if userteamleadername not in sdm_author_dict.keys():
			sdm_author_dict[userteamleadername] = {}
			sdm_author_dict[userteamleadername]['teamleaderusername'] = userteamleadername
			sdm_author_dict[userteamleadername]['userteamleaderid'] = userteamleaderid
			sdm_author_dict[userteamleadername]['userteamleaderemail'] = userteamleaderemail
			if 'sdminfor' not in sdm_author_dict[userteamleadername].keys():
				sdm_author_dict[userteamleadername]['sdminfor'] = []
		sdm_author_dict[userteamleadername]['sdminfor'].append(item) if item not in sdm_author_dict[userteamleadername]['sdminfor'] else ''
	print "patchownerList",patchownerList
	print "emailToList",emailToList
	print sdm_author_dict
	projectid = db.getProjectID(projectname)
	print "projectid",projectid
	taskinfo = db.CreateFatherTask(projectname,updatedSdmDict,sdm_author_dict,projectid,version)
	email = Email()
	if taskinfo:
		email.createEmail(patchownerList,emailToList, projectname, version,taskinfo)







if __name__ == '__main__':  
    main()
