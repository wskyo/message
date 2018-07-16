import os
import pexpect
import re
import sys
import getpass

lastdir = [os.getcwd()]
def pushDir(dir):
    global lastdir
    lastdir.append(os.getcwd())
    print 'chdir %s --> %s' % (lastdir[-1], dir)
    os.chdir(dir)

def popDir():
    global lastdir
    print 'chdir %s --> %s' % (os.getcwd(), lastdir[-1])
    os.chdir(lastdir[-1])
    lastdir.pop(lastdir.__len__()-1)


def docmd(cmd, exp={}, exit=True):
    ask, answer = [], []
    for key, val in exp.items():
        ask.append(key)
        answer.append(val)
    ask.append(pexpect.EOF)
    answer.append(None)
    proc = pexpect.spawn('/bin/bash', ['-c', cmd], timeout=None, logfile=sys.stdout)
    proc.setecho(False)
    while True:
        index = proc.expect(ask)
        if ask[index] == pexpect.EOF:
            break
        else:
            if answer[index]:
                proc.sendline(answer[index])
            else:
                proc.sendline()
    proc.close()
    if proc.exitstatus == 0:
        pass
    else:
        print 'docmd: %s. ERROR<RETURN CODE %s>' % (cmd, proc.exitstatus)
        if exit:
            sys.exit(proc.exitstatus)
    return proc.exitstatus

def getConf(msg=None, val=None,  echo=True):
    metch = re.search(r'<((.*?\|)+.*?)>', msg) if msg else None
    while True:
        sys.stdout.write('\033[1;32m%s :\033[0m' % msg)
        value = sys.stdin.readline().strip() if echo else getpass.getpass('').strip()
        if not value and val:
            return val
        if metch:
            value = value or metch.group(1).partition('|')[0]
            if re.match(r'%s' % metch.group(1).lower(), value.lower()):
                break
        elif value:
            break
    return value
