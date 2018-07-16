#!/usr/bin/python

import os
import sys
import re
import commands
import glob
sys.path.append('/local/int_jenkins/lib')
from Utils import *
from Config import *

conf = Config();
conf.addFromArg(sys.argv[1:])

projDir = '/local/smallversionmgnt/'+conf.getConf('project', 'Project name')
checkDir(os.path.realpath(projDir))

os.chdir(projDir)

cmd = conf.getConf('cmd', 'Command to go')

versionSequence = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

if cmd == 'setbig':
	big = conf.getConf('bignum', 'Big number')
	fp = open('big', 'w+')
	fp.write(big+'\n')
	fp.close()
	fp = open('small', 'w+')
	fp.write('1\n')
	fp.close()

if cmd == 'getcur':
	big = file('big', 'r').read().strip()
	small = file('small', 'r').read().strip()
	print '%s-%s' % (big, small)

if cmd == 'inc':
	small = file('small', 'r').read().strip()
	if small == 'Z':
		print 'Current mall version is already Z !!!'
		sys.exit(1)
	fp = open('small', 'w+')
	fp.write('%s\n' % versionSequence[versionSequence.index(small)+1])
	fp.close()
	big = file('big', 'r').read().strip()
	small = file('small', 'r').read().strip()
	print '%s-%s' % (big, small)

if cmd == 'getlast':
	curVer = conf.getConf('cur', 'Current version', 'none')
	if curVer == 'none':
		big = file('big', 'r').read().strip()
		small = file('small', 'r').read().strip()
	else:
		match = re.match('([^-]+)-([^-]+)', curVer)
		if match:
			big = match.group(1)
			small = match.group(2)
		else:
			print 'Current version error'
			sys.exit(1)
	print '%s-%s' % (big, versionSequence[versionSequence.index(small)-1])
