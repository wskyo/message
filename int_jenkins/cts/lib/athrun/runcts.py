#!/usr/bin/python
##############################
#
##############################
import os
import sys
import pexpect


class runcts:
    def __init__(self, ctspath, sessionid,dvicesid):
        self.ctspath = ctspath
        self.sessionid = sessionid
        self.dvicesid = dvicesid

    def run(self):
        try:
            os.system("chmod 0755 "+self.ctspath)		
            child = pexpect.spawn(self.ctspath)
            child.expect('cts-tf >')
            child.sendline('run cts -s '+ self.dvicesid + ' --continue-session ' + self.sessionid)
            child.interact()
        except OSError:
            sys.exit(0)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print 'Please give the run cts file path!'
        sys.exit()

    if len(sys.argv) == 3:
        rc = runcts(sys.argv[1], '0',sys.argv[2])
    else:
        rc = runcts(sys.argv[1], sys.argv[2],sys.argv[3])

    rc.run()
