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
		mysql = 'SELECT id FROM dotp_tasks_item WHERE task_project_id="%s" and task_type="build error" and task_name="%s" and task_desc="%s"' % (projectid,task_name,task_desc)
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

	def CreateFatherTask(self,projectname,projectid,version,errorInfo):
		task_project_id = projectid
		task_priority = 'P1(Quick)'
		task_type = 'build error'
		task_status = 'ongoing'
		task_desc = errorInfo
		task_owner = 39
		task_start_date = datetime.datetime.now()
		task_planned_date = task_start_date + datetime.timedelta(days =1)
		task_planned_date  = task_planned_date.strftime('%Y-%m-%d %H:%M:%S')		
		task_name = '[%s %s]compile error' % (projectname,version)
		task_assigned = 39
		if self.getParentID(projectid, task_name, task_desc):
			sys.exit(0)
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
		self.CreateSonTask(task_project_id,task_priority,task_type,task_desc,task_owner,parentId,task_name)


	def CreateSonTask(self,task_project_id,task_priority,task_type,task_desc,task_owner,parentId,task_name):
		print "parentId" ,parentId
		task_assigned = task_owner
		task_status = 'ongoing'
		task_start_date = datetime.datetime.now()
		task_planned_date = task_start_date + datetime.timedelta(days =1)
		task_planned_date = task_planned_date.strftime('%Y-%m-%d %H:%M:%S')
		task_block = None
		print 'task_desc',task_desc
		insertsql = "INSERT INTO dotp_tasks_detail  (task_desc,task_owner,task_assigned,task_status,task_start_date,task_planned_date,parentId,task_block) \
		   VALUES('%s','%s','%s','%s','%s','%s','%s','%s') " \
%(task_desc,task_owner,task_assigned,task_status,task_start_date,task_planned_date,parentId,task_block)
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

def main():
	db = CreateTask()
	print "begin create build error type task in prsm"	
	codeBranchName = sys.argv[1]
	projectname = db.getProjectName(codeBranchName)
	version = sys.argv[2]
	errorInfo = sys.argv[3]
	projectid = db.getProjectID(projectname)
	print "projectid",projectid
	taskinfo = db.CreateFatherTask(projectname,projectid,version,errorInfo)

if __name__ == '__main__':  
    main()
