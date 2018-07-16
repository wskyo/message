#!/usr/bin/python
import MySQLdb
from time import strftime, localtime
import datetime
import time
import sys
sys.path.append('/local/int_jenkins/lib')
import common

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
			common.show("Exception:%s\nWhile execute %s" % (e, sql), True)
			sys.exit(1)

	def getAllProjectIDList(self,importbranchName):
		print "importbranchName",importbranchName
		mysql = 'SELECT `project_id` FROM dotp_projects WHERE project_importbranch_name="%s"' % importbranchName
		projectlist = []
		try:
			result = self.query(mysql, False)
			if result:
				for item in result:
					projectlist.append(item[0]) if item[0] not in 	projectlist else ''
					print "projectlist ",projectlist
			else:
				print "There is no projectid in db"
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)
		return projectlist

	def getDesFromProjectID(self,branchname,vnum,pnum,eserciceID):
		filter_info = '[mtk_patch][%s][%s][%s_%s]' % (branchname,eserciceID,vnum,pnum)
		mysql = 'SELECT `id` FROM dotp_manpower WHERE `Describe`="%s"' % filter_info
		print mysql
		importid = ''
		try:
			result = self.query(mysql, True)
			if result:
				importid = result[0]					
				return importid
			else:
				print "There is no mtk patch info in db"

				return False
		except Exception, e:
			print e
			print "connect to WR failed"
			sys.exit(1)


	def getImportID(self, eserciceID):
		mysql = 'SELECT `id` FROM dotp_mtk_import WHERE eservice_ID="%s"' % eserciceID
		importid = ''
		try:
			result = self.query(mysql, True)
			if result:
				importid = result[0]
			else:
				print "There is no importid in db"
		except Exception, e:
			print e
			print "connect to prsm failed"
			sys.exit(1)
		return importid
		
	def insertMtkInfo(self, description, start_time,importbranchname,productid,key_value,userid):
		type_m = 'MTK Import'
		user_id = userid
		team_id = 6
		costtime = 1
		report_comment = '[ImportBranchName]'+importbranchname
		insertsql = "INSERT INTO dotp_manpower (`type`,`Describe`,`KeyValue`,`DateValue`,`CostTime`,`user_id`,`project_id`,`team_id`,`mpw_activity`) \
VALUES('%s','%s','%s','%s',%s, %s, %s, %s,'Integration')" \
%(type_m,description,key_value,start_time,costtime,user_id,productid,team_id)
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


def main():
	print "begin insert info to manpower in prsm"
	print "sys.argv",sys.argv
	db = CreateTask()
	importbranchname = sys.argv[1]
	print 'importbranchname',importbranchname
	vnum = sys.argv[2]
	print 'vnum',vnum
	pnum = sys.argv[3]
	print 'pnum',pnum
        sys.exit(0)
	#mtktype = sys.argv[4]
	#print 'mtktype',mtktype
	eserciceID = sys.argv[4]
	print 'eserciceID',eserciceID
	username = sys.argv[5]
	userid = db.getUserID(username)
	description = '[mtk_patch][%s][%s][%s_%s]' % (importbranchname,eserciceID,vnum,pnum)
	print 'description',description
	date_value = time.strftime('%Y-%m-%d',time.localtime(time.time()))
	projectlist = db.getAllProjectIDList(importbranchname)
	productid = projectlist[0]
	key_value = db.getImportID(eserciceID)
	if db.getDesFromProjectID(importbranchname,vnum,pnum,eserciceID) == False:
		db.insertMtkInfo(description,date_value,importbranchname,productid,key_value,userid)
	else:
		print "The info has been insert before"
	db.close_db()





if __name__ == '__main__':  
    main()
