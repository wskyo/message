import sys
import os
import subprocess
import fcntl
import pexpect
from Utils import *

class DownCode():
	def __init__(self, fastdown='no', fastbase='', fastdir=''):
		self.fastDown = fastdown
		if self.fastDown == 'yes':
			self.fastBase = fastbase
			self.fastDir = fastdir

	def downCode(self, git, manifest, projlist=''):
		if self.fastDown == 'yes':
			if os.path.isdir(self.fastBase+self.fastDir+'/.repo') and os.path.isfile(self.fastBase+self.fastDir+'/lock'):
				print "Trying to get lock..."
				flock = open(self.fastBase+self.fastDir+'/lock')
				fcntl.flock(flock, fcntl.LOCK_EX)
				docmd('ln -s '+self.fastBase+self.fastDir+'/.repo .')
				docmd("rm -f .repo/project.list")
			else:
				print 'Can\'t do fast download, rollback to normal download'
				self.fastDown = 'no'

		child = pexpect.spawn("repo init -u "+git+' -m '+manifest)
		child.logfile = sys.stdout
		while True:
			try:
				child.expect('Your\s+Name\s+\[[^\[\]]+\]:\s*')
				child.sendline()
				child.expect('Your\s+Email\s+\[[^\[\]]+\]:\s*')
				child.sendline()
				child.expect('is\s+this\s+correct\s+\[yes\/no\]\?\s+')
				child.sendline('yes')
			except pexpect.EOF:
				break
			except pexpect.TIMEOUT:
				continue

		docmd_forever('repo sync '+projlist)

		if self.fastDown == 'yes':
			print "Release lock"
			fcntl.flock(flock, fcntl.LOCK_UN)
			flock.close()
