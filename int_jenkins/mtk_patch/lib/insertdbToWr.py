#!/usr/bin/python
import MySQLdb
from time import strftime, localtime
import datetime
import time
import sys
sys.path.append('/local/int_jenkins/lib')
import common


class wrDb:
	def __init__(self):
		self.get_db_connection()

	def get_db_connection(self):
		try:
			common.show("%s Connect to wr database" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
			self.db_conn = MySQLdb.connect(host="10.92.34.55", port=3306, user="int", passwd="int@123",db="WR",charset="utf8")
			self.db_cursor = self.db_conn.cursor()
			return self.db_cursor
		except Exception, e:
			print e
			sys.exit(1)

	def close_db(self):
		common.show("%s Close the connection of WR database..." % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		if self.db_conn:
			common.show('Closed DB connecion.')
			self.db_conn.close()


	def insertReleaseInfo(self, description, start_time,importbranchname):
		product_id = 12
		type_id = 10
		to_team_report = 1
		is_del = 0
		user_id = 80
		status_id = 8
		report_comment = '[ImportBranchName]'+importbranchname
		insertsql = "INSERT INTO  think_int_mtk_import_report  (product_id,type_id,to_team_report,is_del,description,fact_finish_time,user_id,status_id,reporter_comment) \
		   VALUES(%s,'%s','%s','%s','%s','%s','%s',%s,'%s') " \
%(product_id,type_id,to_team_report,is_del,description,start_time,user_id,status_id,report_comment)
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

	def getDesFromProjectID(self,branchname,vnum,pnum):
		product_id = 12
		filter_info = '[mtk_patch][%s][%s_%s]' % (branchname,vnum,pnum)
		mysql = 'SELECT description FROM think_int_mtk_import_report WHERE product_id="%s"' % product_id
		try:
			result = self.query(mysql, False)
			if result:
				for item in result:		
					des = item[0]
					print "des ",des
					if filter_info in des:
						print "mtk patch has been insert"
						return True						
				return False
			else:
				print "There is no mtk patch info in db"
				return False
		except Exception, e:
			print e
			print "connect to WR failed"
			sys.exit(1)



def main():
	print "begin insert release info"
	print "sys.argv",sys.argv
	db = wrDb()
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
	description = '[mtk_patch][%s][%s_%s]' % (eserciceID,vnum,pnum)
	print 'description',description
	start_time = datetime.datetime.now()	
	if db.getDesFromProjectID(importbranchname,vnum,pnum) == False:
		db.insertReleaseInfo(description,start_time,importbranchname)
	db.close_db()
	


if __name__ == '__main__':  
    main()
