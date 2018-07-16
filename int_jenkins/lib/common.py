#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
usage:
    Provider some useful functions.
'''
import sys
import getopt
import os
import re
import pexpect
import smtplib
#import mechanize
import xml.dom.minidom

# dir stack, used to storage the dir change.
__dir_stack = []


def parse_options(argv, docstring, short_opts="", long_opts=[]):
    try:
        opts, args = getopt.getopt(argv, short_opts, long_opts)
    except getopt.GetoptError, err:
        usage(docstring)
        show(str(err), True)
        sys.exit(1)

    parsed_args = {}
    for o, a in opts:
        parsed_args[o] = a

    return parsed_args


def usage(docstring):
    print docstring.rsplit('\n')


def get_conf(parsed_args, short_opt="", long_opt=""):
    value = ""
    if short_opt in parsed_args.keys():
        value = parsed_args[short_opt]
    elif long_opt in parsed_args.keys():
        value = parsed_args[long_opt]
    else:
        show("get argv error.", True)
        sys.exit(1)
    return value


def chdir(path):
    old_dir = os.getcwd()
    os.chdir(path)
    print "chdir %s => %s" % (old_dir, path)
    return old_dir


def push_dir(path):
    global __dir_stack
    __dir_stack.append(chdir(path))


def pop_dir():
    global __dir_stack
    try:
        chdir(__dir_stack.pop())
    except IndexError:
        show("Error: The dir stack is empty.", True)
        sys.exit(1)


def get_user_info(domain, user_conf_file, **kargs):
    user_info = {}
    if not os.path.isfile(user_conf_file):
        show("Can not find %s." % user_conf_file, True)
    for line in file(user_conf_file):
        if re.match('^\s*#', line):
            continue
        info_list = line.split(':')
        try:
            if info_list[3].strip() == domain:
                user_info['name'] = info_list[0].strip()
                user_info['tel'] = info_list[1].strip()
                user_info['mail'] = info_list[2].strip()
                user_info['domain'] = info_list[3].strip()
        except IndexError:
            show("Not well formated %s at line which domain is %s."
                    % (user_conf_file, domain), True)
            sys.exit(1)
    if not user_info:
        show("Could not get the user info of %s" % domain)
        sys.exit(1)
    # add extra info to the user dict.
    for key, value in kargs.items():
        user_info[key] = value
    return user_info


def docmd(cmd):
    proc = pexpect.spawn('/bin/bash', ['-c', cmd], timeout=None)
    proc.expect(pexpect.EOF)
    proc.close()
    if proc.exitstatus != 0:
        show("Error: docmd:%s$ %s <Return %d>\n" % (os.getcwd(),
                                cmd, proc.exitstatus), True)
        sys.exit(1)


def show(msg, error=False):
    print "\033[32;1m==========================\033[0m"
    if error:
        print "\033[31;1m[ERROR]%s\033[0m" % msg
    else:
        print "\033[34;1m[INFO]%s\033[0m" % msg
    print "\033[32;1m==========================\033[0m"


def mail_auth(domain, passwd):
    server = smtplib.SMTP('mail.tcl.com')
    is_auth_success = False
    try:
        server.login('ta-cd/%s' % domain, passwd)
        show("Mail auth success")
        is_auth_success = True
    except smtplib.SMTPAuthenticationError:
        show('Mail auth failed.', True)
        sys.exit(1)
    finally:
        server.quit()
    return is_auth_success


#def bugzilla_auth(loginname, passwd):
    #br = mechanize.Browser()
    #br.set_handle_robots(False)
    #br.set_handle_equiv(False)
    #br.open('http://bugzilla.tcl-ta.com/index.cgi?GoAheadAndLogIn=1')
    #br.select_form(name='login')
    #br['Bugzilla_login'] = loginname
    #br['Bugzilla_password'] = passwd
    #resp = br.submit()
    #is_login_success = False
    #if re.search('Welcome to Bugzilla!', resp.get_data()):
        #show("Bugzilla auth success.")
        #is_login_success = True
    #elif re.search('The username or password you entered is not valid.',
                   #resp.get_data()):
        #show("Bugzilla auth failed.", True)
        #sys.exit(1)
    #br.close()
    #return is_login_success


def version_compare(version_last, version_current, MANIFEST_PATH):
    version_last_dom = xml.dom.minidom.parse("%s/v%s.xml"
        % (MANIFEST_PATH, version_last))
    version_current_dom = xml.dom.minidom.parse("%s/v%s.xml"
        % (MANIFEST_PATH, version_current))
    version_last_list = version_last_dom.getElementsByTagName('project')
    version_current_list = version_current_dom.getElementsByTagName('project')

    last_proj_num = len(version_last_list)
    version_git_list = ['version-cocktail', 'alps/version_babyd', 'version_yarism', 'version_mt6572']
    current_proj_num = len(version_current_list)
    if last_proj_num != current_proj_num:
        return True
    for last_proj in sorted(version_last_list):
        last_proj_name = last_proj.getAttribute('name')
        if last_proj_name in version_git_list or 'version' in last_proj_name:
            continue
        is_find_proj = False
        for current_proj in sorted(version_current_list):
            current_proj_name = current_proj.getAttribute('name')
            if last_proj_name == current_proj_name:
                is_find_proj = True
                last_proj_revision = last_proj.getAttribute('revision')
                current_proj_revision = current_proj.getAttribute('revision')
                if last_proj_revision != current_proj_revision:
                    return True
                break
        if not is_find_proj:
            return True
    for current_proj in sorted(version_current_list):
        current_proj_name = current_proj.getAttribute('name')
        if current_proj_name in version_git_list or 'version' in current_proj_name:
            continue
        is_find_proj = False
        for last_proj in sorted(version_last_list):
            last_proj_name = last_proj.getAttribute('name')
            if current_proj_name == last_proj_name:
                is_find_proj = True
                break
        if not is_find_proj:
            return True
    return False
