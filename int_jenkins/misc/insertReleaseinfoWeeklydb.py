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


class weeklyReportDb:
	def __init__(self):
		self.get_db_connection()		

	def get_db_connection(self):
		try:
			common.show("%s Connect to weekly report database" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
			self.db_conn = MySQLdb.connect(host="10.92.34.55", port=3306, user="int", passwd="int@123",db="WR",charset="utf8") #, charset="gbk"latin1
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
				return False
		except Exception, e:
			print e
			print "connect to WR failed"
			sys.exit(1)


	def getReportComment(self, reporter_id):
		print "reporter_id",reporter_id
		mysql = 'SELECT reporter_comment FROM think_version_release_report WHERE report_id="%s"' % reporter_id
		reporter_comment = ''
		try:
			result = self.query(mysql, True)
			if result:					
				reporter_comment = result[0]
				print "reporter_comment ",reporter_comment									
				return reporter_comment
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
				sys.exit(1)
		except Exception, e:
			print e
			print "connect to WR failed"
			sys.exit(1)


	def insertReleaseInfo(self,productname, description, start_time,version):
		hour = ''
		str_start_time = str(start_time)
		date_of_start_time = str_start_time.split(' ')[0]
		time_of_start_time = str_start_time.split(' ')[1]
		match = re.match('(\d+):(\d+):(\d+)',time_of_start_time)
		if match:
			hour = match.group(1)
			if 14>int(hour)>=9:
				expect_finish_time = start_time + datetime.timedelta(hours =5.5)
			elif 9>int(hour)>=7:
				expect_finish_time = start_time + datetime.timedelta(hours =4)
			elif 16>=int(hour)>=14:
				expect_finish_time = start_time + datetime.timedelta(hours =4)
			elif int(hour)>16:
				expect_finish_time = start_time + datetime.timedelta(hours =16)	
			else:
				expect_finish_time = start_time + datetime.timedelta(hours =4)
		else:
			expect_finish_time = start_time + datetime.timedelta(hours =4)						
		#expect_finish_time = start_time + datetime.timedelta(hours =4)
		product_id = self.getProjectIDFromProjectname(productname)
		type_id = 6
		to_team_report = 1
		is_del = 0
		user_id = 86
		reporter_comment = 'BuildTimes:1'
		report_comment_db = ''
		buildtimes = 1
		buildtimes_new = 1
		if self.getDesFromProjectID(product_id,description) == False:
			insertsql = "INSERT INTO  think_version_release_report  (product_id,type_id,to_team_report,is_del,description,start_time,expect_finish_time,user_id,reporter_comment) \
		   VALUES(%s,'%s','%s','%s','%s','%s','%s',%s,'%s') " \
%(product_id,type_id,to_team_report,is_del,description,start_time,expect_finish_time,user_id,reporter_comment)
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
		else:
			reporter_id = self.getReportID(product_id,description)
			report_comment_db = self.getReportComment(reporter_id)
			if report_comment_db:
				buildtimes = report_comment_db.split(":")[1]
				print "buildtimes",buildtimes
				buildtimes_new = int(buildtimes) + 1
			#if buildtimes_new >1:
				new_comment = 'BuildTimes:%s' % buildtimes_new
				updatesql = 'UPDATE think_version_release_report SET `reporter_comment` = "%s" WHERE report_id = %s '%(new_comment, reporter_id)
				#updatesql = "INSERT INTO  think_version_release_report reporter_comment VALUES '%s'" %(reporter_comment)
				print updatesql
				try:			
					self.db_cursor.execute(updatesql)
					self.db_conn.commit()
		
				except Exception, e:
					print e
			else:
				print "buildtimes",buildtimes
				new_comment = 'BuildTimes:%s' % buildtimes				
				updatesql = "INSERT INTO  think_version_release_report reporter_comment VALUES '%s'" %(reporter_comment)
				print updatesql
				try:			
					self.db_cursor.execute(updatesql)
					self.db_conn.commit()
		
				except Exception, e:
					print e
					
			
			

def main():
	print "begin insert release info"
	print "sys.argv",sys.argv
	db = weeklyReportDb()
	start_time = datetime.datetime.now()
	print 'start_time',start_time
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
	db.insertReleaseInfo(productname,description,start_time,version)
	db.close_db()

if __name__ == '__main__':  
    main()
#python insertReleaseinfoWeeklydb.py pixi4-4_3g 3DH8


