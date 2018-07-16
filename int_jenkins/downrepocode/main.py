#!/usr/bin/python

import os
import sys
import re
import pexpect
import datetime
import glob
import fcntl
from Utils import *
from Config import *


### down or repo code user this python
def __doDownload(repoAddr, branch, manifest, repoPath):
	repoExp = {}
	repoExp['Your\s+Name\s+\[[^\[\]]+\]:\s*'] = '\n'
	repoExp['Your\s+Email\s+\[[^\[\]]+\]:\s*'] = '\n'
	repoExp['is\s+this\s+correct\s+\[y\/n\]\?\s+'] = 'y'
	repoExp['Are\s+you\s+sure\s+you\s+want\s+to\s+continue\s+connecting\s+(y/n)?\s*'] = 'y'
	repoCmd = '%s init -u %s' % (repoPath, repoAddr)
	print '====repo path is: %s====' %repoPath
	print repoCmd
	if branch:
		repoCmd += ' -b %s' % branch
	if manifest:
		repoCmd += ' -m %s' % manifest
	docmd(repoCmd, exp=repoExp)
	docmd('%s sync -j4' % repoPath)

def main():
	conf = Config();
	conf.addFromArg(sys.argv[1:])
	isFast = True if conf.getConf('fastdown', 'Fast download <yes|no>', 'yes') == 'yes' else False
	repoAddr = conf.getConf('repoaddress', 'Url address for repo repository')
	branch = conf.getConf('branch', 'Manifest branch', 'none')
	manifest = conf.getConf('manifest', 'Manifest file name', 'none')
	repoPath = conf.getConf('repopath', 'repo tool path', '/local/tools/repo/repo')

	if branch == 'none':
		branch = ''

	if manifest == 'none':
		manifest = ''

	if isFast:
		cacheDir = conf.getConf('cachedir', 'Cache dir {^/}')

		if not os.path.isfile('%s/lock' % cacheDir):
			docmd('rm -rf %s' % cacheDir)
			checkDir(cacheDir)
			docmd('touch %s/lock' % cacheDir)
			print 'Trying to get lock...'
			flock = open('%s/lock' % cacheDir)
			fcntl.flock(flock, fcntl.LOCK_EX)
			__doDownload(repoAddr, branch, manifest, repoPath)
			docmd('mv .repo %s/repo' % cacheDir)
			fcntl.flock(flock, fcntl.LOCK_UN)
			flock.close()
			for fileName in glob.glob('*') + glob.glob('.*'):
				docmd('rm -rf %s' % fileName)

		print 'Trying to get lock...'
		flock = open('%s/lock' % cacheDir)
		fcntl.flock(flock, fcntl.LOCK_EX)

		gitCacheNeedRemove = conf.getConf('gitcacheneedremove', 'Git in cache dir need to remove', 'none')
		if gitCacheNeedRemove != 'none':
			 for oneGit in gitCacheNeedRemove.split(','):
				 docmd('rm -rf "%s/repo/projects/%s"' % (cacheDir, oneGit.strip()))

		docmd('ln -s %s/repo .repo' % cacheDir)
		###second down load will didn't down repo
		docmd('rm -f .repo/project.list')

	__doDownload(repoAddr, branch, manifest, repoPath)

	if isFast:
		print 'Release lock'
		fcntl.flock(flock, fcntl.LOCK_UN)
		flock.close()

if __name__ == '__main__':
	main()
