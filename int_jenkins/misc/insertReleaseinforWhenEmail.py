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


class weeklyReportDbEamil:
	def __init__(self):
		self.get_db_connection()		

	def get_db_connection(self):
		try:
			common.show("%s Connect to weekly report database" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
			self.db_conn = MySQLdb.connect(host="10.92.34.55", port=3306, user="int", passwd="int@123",db="WR",charset="utf8")
			self.db_cursor = self.db_conn.cursor()
			return self.db_cursor
		except Exception, e:
			print e
			sys.exit(1)

	def close_db(self):
		common.show("%s Close the connection of  weekly report database..." % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		if self.db_conn:
			common.show('Closed DB connecion.')
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

	def getProjectIDFromProjectname(self, projectname):
		print "projectname",projectname
		mysql = 'SELECT product_id FROM think_product WHERE product_name="%s"' % projectname
		try:
			result = self.query(mysql, True)
			if result:				
				projectid = result[0]
				print "projectid ",projectid				
				return projectid
			else:
				print "the projectid should be existing in db"
				sys.exit(1)
		except Exception, e:
			print e
			print "connect to WR failed"
			sys.exit(1)


	def getUserIDFromUsername(self, username):
		print "username",username
		mysql = 'SELECT user_id FROM think_user WHERE user_name="%s"' % username
		try:
			result = self.query(mysql, True)
			if result:				
				userid = result[0]
				print "userid ",userid				
				return userid
			else:
				print "the userid should be existing in db"
				sys.exit(1)
		except Exception, e:
			print e
			print "connect to WR failed"
			sys.exit(1)

	def getDesFromProjectID(self, product_id,version):
		print "product_id",product_id
		mysql = 'SELECT description FROM think_version_release_report WHERE product_id="%s"' % product_id
		try:
			result = self.query(mysql, False)
			if result:
				for item in result:		
					des = item[0]
					print "des ",des
					if version in des:
						print "release info db exist"
						return True						
				return False
			else:
				print "the userid should be existing in db"
				sys.exit(1)
		except Exception, e:
			print e
			print "connect to WR failed"
			sys.exit(1)

	def getReportID(self, product_id,description):
		print "product_id",product_id
		print "description",description
		reportid = ''
		mysql = 'SELECT report_id FROM think_version_release_report WHERE product_id="%s" and description="%s"' % (product_id,description)
		try:
			result = self.query(mysql, True)
			if result:					
				reportid = result[0]
				print "reportid ",reportid					
				return reportid
			else:
				print "the reportid should be existing in db"
				return
		except Exception, e:
			print e
			print "connect to WR failed"
			sys.exit(1)


	def getexpect_finish_time(self, reportid):
		print "reportid",reportid
		expect_finish_time = ''
		mysql = 'SELECT expect_finish_time FROM think_version_release_report WHERE report_id="%s"' % reportid
		try:
			result = self.query(mysql, True)
			if result:					
				expect_finish_time = result[0]
				print "expect_finish_time ",expect_finish_time					
				return expect_finish_time
			else:
				print "the reportid should be existing in db"
				sys.exit(1)
		except Exception, e:
			print e
			print "connect to WR failed"
			sys.exit(1)


	def insertReleaseInfo(self,productname, description, start_time,version):
		expect_finish_time = start_time + datetime.timedelta(hours =4)
		product_id = self.getProjectIDFromProjectname(productname)
		type_id = 6
		to_team_report = 1
		is_del = 0
		if self.getDesFromProjectID(product_id,version) == False:
			insertsql = "INSERT INTO  think_version_release_report  (product_id,type_id,to_team_report,is_del,description,start_time,expect_finish_time) \
		   VALUES(%s,'%s','%s','%s','%s','%s','%s') " \
%(product_id,type_id,to_team_report,is_del,description,start_time,expect_finish_time)
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


	def updateReleaseInfolast(self,last_des,user_id,reportid,fact_finish_time,product_id):
		print 'fact_finish_time',fact_finish_time 
		#product_id = self.getProjectIDFromProjectname(productname)
		type_id = 6
		to_team_report = 1
		is_del = 0
		status_id = 8
		expect_time = self.getexpect_finish_time(reportid)
		if fact_finish_time > expect_time:
			status_id = 14
		#if self.getDesFromProjectID(product_id,version) == True:
		updatesql = 'UPDATE think_version_release_report SET `fact_finish_time` = "%s",`user_id` = "%s", `description` = "%s" ,`status_id` = "%s" WHERE report_id = "%s" '%(fact_finish_time,user_id,last_des,status_id,reportid)
		print updatesql
		try:			
			self.db_cursor.execute(updatesql)
			self.db_conn.commit()
		
		except Exception, e:
			print e

def main():
	print "begin insert release info"
	print "sys.argv",sys.argv
	db = weeklyReportDbEamil()
	productname = sys.argv[1]
	print 'productname',productname
	version = sys.argv[2]
	print 'version',version
	if len(version) > 4:
		versionType = productname
		productname = 'GAPK'
	else:
		if version[2] < 'N' and not version.__contains__('-'):
			versionType = 'CU'
		elif version[2] >= 'N' and not version.__contains__('-'):
			versionType = 'MINI'
	description = '[%s][%s]' % (versionType,version)
	print 'description',description
	reportid = ''
	comment = sys.argv[3]
	username = sys.argv[4]
	#if username == 'liyun.liu':
		#username = 'liyun.liu.hz'
	#fact_finish_time  = sys.argv[5]
	fact_finish_time  = datetime.datetime.now()
	user_id = db.getUserIDFromUsername(username)
	last_des = description + comment
	product_id = db.getProjectIDFromProjectname(productname)
	if db.getDesFromProjectID(product_id,description) == True:
		reportid = db.getReportID(product_id,description)
	if reportid:
		db.updateReleaseInfolast(last_des,user_id,reportid,fact_finish_time,product_id)
	db.close_db()
	


if __name__ == '__main__':  
    main()
#python insertReleaseinforWhenEmail.py pixi4-4_3g 3DH6 "release for spm" xiaoling.luo






