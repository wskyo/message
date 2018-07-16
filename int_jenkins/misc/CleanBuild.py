#!/usr/bin/python
import sys
import re
from commands import getoutput
import os

BUILD_DIR=""

def checkDist(buildpath):
	print 'check disk space!'
	flag = False
	print buildpath
	space = getoutput('df -h %s | awk \'{print $4, $5}\'' %buildpath)
	print "====%s====" % space
	space = space.split('\n')[1]
	match = re.search(r'^(\d+[TGP])\s(\d+%)$', space)
	if match:
		space = match.groups()
        else:
        	space = space.split(' ')
        if float(space[1][:-1]) > 93:
        	flag = True
                #self.sendDiskNotice(space)
        if space[0][-1] in 'TP':
        	return flag
        elif space[0][-1] == 'G' and float(space[0][:-1]) > 60:
        	return flag
        else:
		print 'not enough disk left: %s' % space[0]
        	sys.exit(1)
	return flag

def cleanBefore():
        print 'find /local/build/*release/v* -maxdepth 0 -type d -mtime +14 -exec rm -rf {} \;'
        out = os.system('find /local/build/*release/v* -maxdepth 0 -type d -mtime +14 -exec rm -rf {} \;')
        if out != 0:
            print 'do find /local/build/*release/v* -maxdepth 0 -type d -mtime +14 -exec rm -rf {} \; ERROR'
        print 'find /local/release/*/v* -maxdepth 0 -type d -mtime +14 -exec rm -rf {} \;'
        out = os.system('find /local/release/*/v* -maxdepth 0 -type d -mtime +14 -exec rm -rf {} \;')
        if out != 0:
            print 'do find /local/release/*/v* -maxdepth 0 -type d -mtime +14 -exec rm -rf {} \; ERROR'
        print 'find /local/black/*/v* -maxdepth 0 -type d -mtime +14 | xargs rm -rf'
        out = os.system('find /local/black/*/v* -maxdepth 0 -type d -mtime +14 | xargs rm -rf')
        if out != 0:
            print 'do find /local/black/*/v* -maxdepth 0 -type d -mtime +14 | xargs rm -rf ERROR'

if __name__ == '__main__':
	if sys.argv[1]=='-builddir':
		BUILD_DIR = sys.argv[2]
		cleanBefore()
		checkDist(BUILD_DIR)
