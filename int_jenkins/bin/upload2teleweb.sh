#!/usr/bin/python

import sys
import os
import re
sys.path.append('/local/int_jenkins/lib')
import pexpect
####################################################################
#user to upload teleweb using this script
####################################################################


def uploadToTeleweb(releaseName,dst,telewebPwd):
	## if version file is exit, delete it
	cmdRm='ssh sl_hz_hran@10.92.32.26 rm -rfv /mfs/teleweb/%s' %dst
	childRm = pexpect.spawn(cmdRm)
	childRm.logfile = sys.stdout
	while True:
	    try:
		childRm.expect("sl_hz_hran@10.92.32.26's password:")
		childRm.sendline(telewebPwd)
	    except pexpect.EOF:
		break
	    except pexpect.TIMEOUT:
		continue

	cmdScp='scp -vr %s sl_hz_hran@10.92.32.26:/mfs/teleweb/%s' % (releaseName, dst)

	childScp = pexpect.spawn(cmdScp)
	childScp.logfile = sys.stdout
	while True:
	    try:
		childScp.expect("sl_hz_hran@10.92.32.26's password:")
		childScp.sendline(telewebPwd)
	    except pexpect.EOF:
		break
	    except pexpect.TIMEOUT:
		continue

	print 'upload to Teleweb'

def HelpInfo():
	print "pls input right paraments!"

if __name__ == '__main__':
	if len(sys.argv) != 3:
		HelpInfo()
	else:
		uploadToTeleweb(sys.argv[1], sys.argv[2], 'lin@321')
