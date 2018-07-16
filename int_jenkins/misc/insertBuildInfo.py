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


def get_project_id(conn,projectname):
	try:
		
		sql = "select ID from project_base_info where ProjectName ='%s'" %projectname
		dotpdb_cursor = conn.cursor(MySQLdb.cursors.DictCursor)
		dotpdb_cursor.execute(sql)
		result = dotpdb_cursor.fetchone()
		print result
		buildid = ''
		if result:
			buildid = result['ID']
			print buildid
			return buildid
	    	dotpdb_cursor.close()
	except Exception, e:
		print e
		print 'get project error!!!'
    		sys.exit(0)


def insert_build_history(conn,projectid,manifestBranch,curVer,buildtype,releasenote,spm,owner,patchlevel,gmsversion,releasegms,gmsdeadline,ctsversion,ctsdeadline,gtsversion,gtsdeadline):

	Purpose ='upgrade'
	if len(curVer)!=4:
		Purpose ='Test'
	currTimeStamp = datetime.datetime.now()- datetime.timedelta(minutes=50)
	strCurrTime = currTimeStamp.strftime("%Y-%m-%d %H:%M:%S")
	insertsql = "INSERT INTO release_version_info  (ProjectID,Version,ReleaseTime,SDDPerso,CSPath,ResourceModify,RequestExcel,UploadTime,UploadUserID,AskPerson,Purpose,IsBlack,Branch,ReleaseNote,SecurityPatchLevel,GMSVersion,GMSNewVersion,GMSDeadline,GoogleCTSTestVersion,GoogleCTSNewVersionDeadline,GoogleGTSTestVersion,GoogleGTSNewVersionDeadline) \
		   VALUES(%s,'%s','%s','%s','','','','%s',47,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " \
%(projectid,curVer,strCurrTime,owner,strCurrTime,spm,Purpose,buildtype,manifestBranch,releasenote,patchlevel,gmsversion,releasegms,gmsdeadline,ctsversion,ctsdeadline,gtsversion,gtsdeadline)

	print insertsql
	try:
		dotpdb_cursor = conn.cursor()
		dotpdb_cursor.execute(insertsql)
		conn.commit();
	except Exception, e:
		print e
		print "insert error!!!"
		dotpdb_cursor.close()
		conn.close()
    		sys.exit(0)



def update_build_history(conn,project,manifestBranch,curVer,versiontype):

	currTimeStamp = datetime.datetime.now()
	strCurrTime = currTimeStamp.strftime("%Y-%m-%d %H:%M:%S")
	
        sql ='SELECT ID FROM release_version_info WHERE project ="%s" and branch="%s" and version="%s" ORDER BY UploadTime DESC limit 1 ' %(project,manifestBranch,curVer)
	try:

		dotpdb_cursor = conn.cursor(MySQLdb.cursors.DictCursor)
		dotpdb_cursor.execute(sql)
                result = dotpdb_cursor.fetchone()
		print result
		buildid = ''
		if result:
			buildid = result['ID']
			print buildid
            	dotpdb_cursor.close()
		if buildid != '':
        		updatesql  ='UPDATE release_version_info SET `UploadTime` = "%s" WHERE ID = "%s" '%(strCurrTime,buildid)
			print 	updatesql		
			dotpdb_cursor = conn.cursor()
		   	dotpdb_cursor.execute(updatesql)
        	    	conn.commit();
        	    	dotpdb_cursor.close()	

	except Exception, e:
		print e
		print "update error!!!"
		dotpdb_cursor.close()
		conn.close()
    		sys.exit(0)




#/local/int_jenkins/misc/insertBuildInfo.py -version 1A29 -Project pixi353g -manifestbranch pixi3-5-v1.0-dint -versiontype CU -releasenote ReleaseNote_pixi3-5_3g_SW1A29.xls
def main():
	print "begin wirte build History"
	try:
		dotp_conn=MySQLdb.connect('10.92.35.61', port=3306, user='Int', passwd='Int@123', db='prs')
		#dotp_conn=MySQLdb.connect('127.0.0.1', port=3306, user='root', passwd='tcl@123', db='prs')
	except Exception, e:
		print e
		print "connect DB error!!!"
    		sys.exit(0)

	conf = Config()
	conf.addFromArg(sys.argv[1:])
	curVer = conf.getConf('version', 'Current version {^[0-9A-Z]{3}-[1-9A-Z]$}')
	project = conf.getConf('Project', 'project name')
	manifestBranch = conf.getConf('manifestbranch', 'Branch for manifest file git', 'master')
	versiontype = conf.getConf('versiontype', 'versiontype{cu|mini|black|Daily_Version}', 'cu')
	releasenote = conf.getConf('releasenote', 'releasenote', '')
	spm = conf.getConf('spm', 'spm', '')
	owner = conf.getConf('owner', 'owner', '')
	patchlevel = conf.getConf('patchlevel', 'PLATFORM security patch value', '')
	gmsversion = conf.getConf('gmsversion', 'GMS value from code', '')
	releasegms = conf.getConf('releasegms', 'google released lastest gms version', '')
	gmsdeadline = conf.getConf('gmsdeadline', 'google released lastest gms version deadline', '')
	ctsversion = conf.getConf('ctsversion', 'google cts test version', '')
	ctsdeadline = conf.getConf('ctsdeadline', 'google cts test version deadline', '')
	gtsversion = conf.getConf('gtsversion', 'google gts test version', '')
	gtsdeadline = conf.getConf('gtsdeadline', 'google gts test versiondeadline', '')
	projectId = get_project_id(dotp_conn,project)
	if ctsdeadline == 'NA':
		ctsdeadline = '0000-00-00'
	if gtsdeadline == 'NA':
		gtsdeadline = '0000-00-00'
	if projectId !='':
		print "begin build History complete!!!"
		insert_build_history(dotp_conn,projectId,manifestBranch,curVer,versiontype,releasenote,spm,owner,patchlevel,gmsversion,releasegms,gmsdeadline,ctsversion,ctsdeadline,gtsversion,gtsdeadline)
		print "insert build History complete!!!"
	else:
		print "get projectId failed!!!"
	dotp_conn.close()


if __name__ == '__main__':  
    main() 




