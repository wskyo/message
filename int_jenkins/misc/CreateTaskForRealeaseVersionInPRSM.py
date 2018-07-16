#!/usr/bin/python
#coding=utf-8
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

	def CreateFatherTaskForRelease(self,projectname,projectid,version,description,task_desc):
		task_project_id = projectid
		task_priority = 'P1(Quick)'
		task_type = 'release'
		task_status = 'ongoing'
		task_owner = 39
		task_assigned = 39 
		task_start_date = datetime.datetime.now()
		task_planned_date = task_start_date + datetime.timedelta(days =1)
		task_planned_date  = task_planned_date.strftime('%Y-%m-%d %H:%M:%S')
		str_start_time = str(task_start_date)
		date_of_start_time = str_start_time.split(' ')[0]
		time_of_start_time = str_start_time.split(' ')[1]
		match = re.match('(\d+):(\d+):(\d+)',time_of_start_time)
		task_block = 'None'		
		if match:
			hour = match.group(1)
			if 14>int(hour)>=9:
				expect_finish_time = task_start_date + datetime.timedelta(hours =5.5)
			elif 9>int(hour)>=7:
				expect_finish_time = task_start_date + datetime.timedelta(hours =4)
			elif 16>=int(hour)>=14:
				expect_finish_time = task_start_date + datetime.timedelta(hours =4)
			elif int(hour)>16:
				expect_finish_time = task_start_date + datetime.timedelta(hours =16)	
			else:
				expect_finish_time = task_start_date + datetime.timedelta(hours =4)
		else:
			expect_finish_time = task_start_date + datetime.timedelta(hours =4)

		parentId = self.getParentID(projectid, description, task_desc)		
		if not parentId:			
			insertsql = "INSERT INTO dotp_tasks_item  (task_project_id,task_priority,task_type,task_name,task_status,task_owner,task_assigned,task_start_date,task_planned_date,task_block,task_desc) \
		   VALUES(%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " \
%(projectid,task_priority,task_type,description,task_status,task_owner,task_assigned,task_start_date,expect_finish_time,task_block,task_desc)
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
			
		parentId = self.getParentID(projectid, description, task_desc)
		sontaskid = self.getSonID(parentId,task_desc)
		print 'sontaskid',sontaskid
		buildtimes = 'BuildTimes:1'
		if not sontaskid:			
			self.CreateSonTask(task_project_id,task_owner,task_start_date,expect_finish_time,parentId,task_desc,buildtimes)
		else:
			self.UpdateSonTask(sontaskid,buildtimes)			
			

	def CreateSonTask(self,task_project_id,task_owner,task_start_date,expect_finish_time,parentId,task_desc,buildtimes):
		task_assigned = task_owner
		task_status = 'ongoing'
		task_block = None
		insertsql = "INSERT INTO dotp_tasks_detail  (task_desc,task_owner,task_assigned,task_status,task_start_date,task_planned_date,parentId,task_block,task_comment) \
		   VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s') " \
%(task_desc,task_owner,task_assigned,task_status,task_start_date,expect_finish_time,parentId,task_block,buildtimes)
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

	def UpdateSonTask(self,sontaskid,buildtimes):
		comment = self.getsonTaskComment(sontaskid)
		buildnumber = comment.split(":")[1]
		print "buildnumber",buildnumber
		buildtimes_new = int(buildnumber) + 1
		new_comment = 'BuildTimes:%s' % buildtimes_new
		updatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		insertsql = 'UPDATE dotp_tasks_detail SET `task_comment` = "%s",`updatetime`="%s" WHERE id = "%s"' % (new_comment,updatetime,sontaskid)
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

	def getsonTaskComment(self, sontaskid):
		mysql = 'SELECT task_comment FROM dotp_tasks_detail WHERE id="%s"' % sontaskid
		try:
			result = self.query(mysql, True)
			print result			
			if result:
				comment = result[0]
				print "comment ",comment				
				return comment
			else:
				print "the comment should be existing in db"
				return 
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)

	def getParentID(self, projectid, task_name, task_desc):
		mysql = 'SELECT id FROM dotp_tasks_item WHERE task_project_id="%s" and task_type="release" and task_name="%s" and task_desc="%s" and  task_status="ongoing"' % (projectid,task_name,task_desc)
		try:
			result = self.query(mysql, True)
			print result			
			if result:
				ParentID = result[0]
				print "ParentID ",ParentID				
				return ParentID
			else:
				print "the ParentID should be existing in db"
				return 
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)

	def getSonID(self, parentId, task_desc):
		print "task_desc",task_desc
		mysql = 'SELECT id FROM dotp_tasks_detail WHERE parentId="%s" and task_desc="%s"' % (parentId,task_desc)
		try:
			result = self.query(mysql, True)
			print result			
			if result:
				SonID = result[0]
				print "SonID ",SonID				
				return SonID
			else:
				print "the SonID should be existing in db"
				return 
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)


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

	def updateTaskAssinerAndTime(self,parentId,require,userid):
		print 'parentId,require,integrator',parentId,require,userid
		des = self.getdes(parentId)
		des = des + require.decode('utf-8')
		task_end_date = datetime.datetime.now()
		updatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		updatesql = 'UPDATE dotp_tasks_detail SET `task_percent_complete`="100",`task_assigned`="%s",`task_desc`="%s",`task_status`="closed",`task_end_date`="%s",`updatetime` = "%s" WHERE parentId="%s" AND `task_desc`="[INT version release]"' % (userid, des,task_end_date,updatetime,parentId)
		print updatesql
		try:			
			self.db_cursor.execute(updatesql)
			self.db_conn.commit()		
		except Exception, e:
			print e

		f_task_assigned = '39,'+str(userid)
		updatesql = 'UPDATE dotp_tasks_item SET `task_assigned`="%s",`updatetime` = "%s" WHERE id="%s"' % (f_task_assigned,updatetime,parentId)
		print updatesql
		try:			
			self.db_cursor.execute(updatesql)
			self.db_conn.commit()		
		except Exception, e:
			print e

		close = self.getAllSonTaskIDStatus(parentId)
		print "close",close
		if close:			
			updatesql = 'UPDATE dotp_tasks_item SET `task_status`="closed" ,`updatetime` = "%s" WHERE id="%s"' %(updatetime,parentId)
			print updatesql
			try:			
				self.db_cursor.execute(updatesql)
				self.db_conn.commit()		
			except Exception, e:
				print e
		return des

	def insertInfoToManpower(self,projectid,des,userid,taskname,parentId,version):
		print 'projectid,des,integrator',parentId,des,userid
		date_value = time.strftime('%Y-%m-%d',time.localtime(time.time()))
		descri = des + ":" + taskname
		if len(version) > 4:
			costtime = 1
		else:
			costtime = 2
		team_id = 6
		type_m = 'release'
		sontaskid = self.getSonID(parentId,taskname)
		insertsql = "INSERT INTO dotp_manpower (`type`,`Describe`,`KeyValue`,`DateValue`,`CostTime`,`user_id`,`project_id`,`team_id`,`mpw_activity`) \
VALUES('%s','%s','%s','%s',%s, %s, %s, %s,'Integration')" \
%(type_m,descri,sontaskid,date_value,costtime,userid,projectid,team_id)
		print insertsql
		try:			
			self.db_cursor.execute(insertsql)
			self.db_conn.commit()		
		except Exception, e:
			print e

	def getUserID(self, username):
		mysql = 'SELECT user_id FROM dotp_users WHERE user_username="%s"' % username
		try:
			result = self.query(mysql, True)
			print result			
			if result:				
				userid = result[0]
				print "userid ",userid				
				return userid
			else:
				print "the userteamid should be existing in db"
				sys.exit(1)
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)


	def getAllSonTaskIDStatus(self, parentId):
		mysql = 'SELECT task_status FROM dotp_tasks_detail WHERE parentId="%s"' % parentId
		close = True
		try:
			result = self.query(mysql, False)
			print result			
			if result:
				for eachItem in result[0]:
					print "eachItem",eachItem
					if eachItem != "closed":
						close = False	
						break				
			else:
				print "the status should be existing in db"
				sys.exit(1)
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)
		return close


	def getdes(self, parentId):
		mysql = 'SELECT task_desc FROM dotp_tasks_item WHERE id="%s"' % parentId
		try:
			result = self.query(mysql, True)
			print result			
			if result:				
				task_desc = result[0]
				print "task_desc ",task_desc				
				return task_desc
			else:
				print "the task_desc should be existing in db"
				sys.exit(1)
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)

def main():
	db = CreateTask()
	print "begin create task for release version in prsm"
	codeBranchName = sys.argv[1]
	version = sys.argv[2]
	release_type = sys.argv[3]
	print 'version',version
	if len(version) > 4:
		versionType = codeBranchName
		projectname = 'SWD1_Inhouse_APK'
	else:
		if version[2] < 'N' and not version.__contains__('-'):
			versionType = 'CU'
		elif version[2] >= 'N' and not version.__contains__('-'):
			versionType = 'MINI'
		projectname = db.getProjectName(codeBranchName)
	description = '[%s][%s]' % (versionType,version)	
	projectid = db.getProjectID(projectname)
	task_desc = '[INT version release]'
	print "projectid",projectid
	if release_type == "start_build":
		db.CreateFatherTaskForRelease(projectname,projectid,version,description,task_desc)
	elif release_type == "release":
		require = sys.argv[4]
		integrator = sys.argv[5]
		#if integrator == 'liyun.liu':
			#integrator = 'liyun.liu.hz'
		parentId = db.getParentID(projectid, description, task_desc)
		if parentId:
			userid = db.getUserID(integrator)		
			db.updateTaskAssinerAndTime(parentId,require,userid)
			des = task_desc + require.decode('utf-8')
			#db.insertInfoToManpower(projectid,description,userid,des,parentId,version)

if __name__ == '__main__':  
    main()
