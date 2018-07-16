#!/usr/bin/python
import pexpect
import os
import sys
def run():
	checksum = "/local/int_jenkins/TclCheckSum/CheckSum_Gen.exe"
	#os.system('wine %s' % checksum)
	try:    					
		child = pexpect.spawn("wine %s" % checksum)
		print "Start to gen"
		child.expect('')
		child.sendline('y')
		print "End to gen"
		child.interact()
	except OSError:
		sys.exit(0)

def main():
	run()


if __name__ == '__main__':  
	main() 




