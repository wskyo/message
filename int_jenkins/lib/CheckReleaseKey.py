#!/usr/bin/python

import os 
import sys
from commands import *
import re
from Utils import *

class CheckReleaseKey:
	def __init__(self, releaseDir):
		self.rel = releaseDir
		self.nowdir = os.getcwd()
	def checkKey(self):
		tmpdir = '/local/checkRelease'
		if os.path.exists(tmpdir+'/sys'):
			print '/local/checkRelease/sys has been exists'
			docmd('rm -rf '+tmpdir+'/sys')
		docmd('mkdir -p /local/checkRelease/sys')
		os.chdir(tmpdir+'/sys')
		docmd('pwd')
		if os.path.isfile('%s/system.img'%self.rel):
			docmd('cp %s/system.img .'%self.rel)
		else:
			print '++++It can not find system.img++++'
			sys.exit(1)
		docmd('cp /local/tools_int/bin/unyaffs .')
		docmd('unyaffs system.img')
		os.chdir('etc/security')
		docmd('pwd')
		docmd('unzip otacerts.zip')
		print '--------unzip over---------'
		newpath='/local/checkRelease/sys/etc/security/build/target/product/security'
		if os.path.exists(newpath):
			os.chdir(newpath)
		else:
			print '++++++++++++++++++++++++++++++++++++'
			print 'System.img is not signed by releasekey'
			print 'no local/checkRelease/sys/etc/security/build/target/product/security path'
			print '++++++++++++++++++++++++++++++++++++'
			sys.exit(1)
		docmd('pwd')
		if os.path.isfile('releasekey.x509.pem') or os.path.isfile('releasekey.pem'):
			print 'System.img is signed by releasekey'
		else:
			print '++++++++++++++++++++++++++++++++++++'
			print 'System.img is not signed by releasekey'
			print '++++++++++++++++++++++++++++++++++++'
			sys.exit(1)
		print '++++++Start Check Recovery++++++++'
		os.chdir(tmpdir)
		docmd('pwd')
		if os.path.exists(tmpdir+'/rec'):
			print '/local/checkRelease/rec has been exists'
			docmd('rm -rf '+tmpdir+'/rec')
		docmd('mkdir -p rec')
		os.chdir(tmpdir+'/rec')
		docmd('pwd')
		if os.path.isfile('%s/recovery.img'%self.rel):
			docmd('cp %s/recovery.img .'%self.rel)
		else:
			print '++++It can not find recovery.img++++'
			sys.exit(1)
		docmd('. /local/tools_int/bin/ramdisk_from_bootimg.sh unpack . recovery.img')
		print '----unpack finish-----'
		if os.path.exists(tmpdir+'/rec/ramdisk/res'):
			os.chdir(tmpdir+'/rec/ramdisk/res')
			docmd('cat keys >> log.txt')
			f = open('log.txt')
			for line in f.readlines():
				if line.find('1795090719') != -1:
					print 'recovery.img  contains 1795090719,'
					print '++++++++++++++++++++++++++++++++++++'
					print 'recovery.img is not signed by releasekey'
					print '++++++++++++++++++++++++++++++++++++'
					sys.exit(1)
				else:
					print 'recovery.img is signed by releasekey'
					
			f.close()
			os.chdir(self.nowdir)
			docmd('rm -rf /local/checkRelease')
		else:
			print '++++++++++++++++++++++++++++++++++++'
			print 'recovery.img is not signed by releasekey'
			print 'no rec/ramdisk/res path'
			print '++++++++++++++++++++++++++++++++++++'
			sys.exit(1)
		
if __name__ == '__main__':
	chekRelease = CheckReleaseKey('/local/release/mojitolite/vF48')
	chekRelease.checkKey()

