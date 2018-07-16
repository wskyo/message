#!/usr/bin/python
import os
import sys
import re
import pty
sys.path.append('/local/int_jenkins/lib')
from commands import *
import commands

def getScatFilename():
	os.chdir("..")
	scatname = getoutput('ls | grep .*.sca')
	print "scatname",scatname
	match =  re.match('(.*).sca',scatname)
	checkini_name = ''
	if match:
		checkini_name = match.group(1)
		print "the checkini name is ", checkini_name
	os.system('ln -s flashtool/Checksum.ini checksum_%s.ini' % checkini_name)


def main():
	pty.spawn("python /local/int_jenkins/misc/checkSumExe.py".split())
	#os.system('python /local/int_jenkins_clean/int_jenkins/misc/checkSumExe.py')
	getScatFilename()

if __name__ == '__main__':  
	main() 

