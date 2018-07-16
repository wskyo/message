#!/usr/bin/python
# coding: utf-8
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from time import strftime, localtime
from Utils import *
from xlwt import *
from xlrd import open_workbook
from xlutils.copy import copy
import commands
import urllib
import urllib2
import threading
import json
import re
from copy import deepcopy
from dotProjectDb import *
from checkPatchInfor import *


class Patch:
    def __init__(self):
        self.name = ''
        self.no = ''
        self.eservice = ''
        self.owner = ''
        self.type = ''

    @staticmethod
    def getInstance(file, project):
        print file
        patch = Patch()
        patch.name = file
        patch.name_cmd = patch.name.replace('(', '\(').replace(')', '\)')
        patch.name_pms = patch.name.replace('(', '_').replace(')', '_')
        match = re.search(r'(ALPS\d+)\(For_%s_%s_P(\d+)\)\.tar\.gz' % (project.Mproject, project.MPRelease), file)
        print r'(ALPS\d+)\(For_%s_%s_P(\d+)\)\.tar\.gz' % (project.Mproject, project.MPRelease), match
        if match:
            print file
            if project.curPatchNo >= int(match.group(2)):
                return None
            patch.no = match.group(2)
            patch.eservice = match.group(1)
            patch.type = 'common'
        if project.modem_param:
            for key, value in project.modem_param.iteritems():
                key_p = key.replace('(', '\(').replace(')', '\)').replace('.', '\.').replace('{', '\{').replace('}', '\}').replace('*', '\*').replace('+', '\+')
                print '(MOLY\d+)?.*?%s.*?P(\d+).*?\.tar\.gz' % key_p
                match = re.search(r'(MOLY\d+)?.*?%s.*P(\d+).*?\.tar\.gz' % key_p, file)
                print match
                if match:
                    if value[1] >= int(match.group(2)):
                        return None
                    patch.no = match.group(2)
                    patch.eservice = match.group(1) or 'unknown'
                    patch.type = 'modem'
                    break

        else:
            print hasattr(project, 'MmodemProj'), project.MmodemProj, file.__contains__(project.MmodemProj)
            if hasattr(project, 'MmodemProj') and project.MmodemProj and file.__contains__(project.MmodemProj):
                if file.__contains__('MOLY'):
                    print '(MOLY\d+)?.*?%s.*?P(\d+).*?\.tar\.gz' % (project.MmodemProj)
                    match = re.search(r'(MOLY\d+)?.*?%s.*?P(\d+).*?\.tar\.gz' % (project.MmodemProj), file)
                    if match:
                        print file
                        if project.modemCurNo >= int(match.group(2)):
                            return None
                        patch.no = match.group(2)
                        patch.eservice = match.group(1) or 'unknown'
                        patch.type = 'modem'
                    
            else:
                match = re.search(r'.*%s.*P(\d+).*?\.tar\.gz' % project.MmodemProj, file)
        if not patch.no:
            print 'Patch instance Error!!'
            raise Exception('Patch instance Error')
        else:
            patch.name_P = 'P%s_%s' % (patch.no, patch.name_pms) if patch.type == 'common' else patch.name_pms
            return patch


class Project(object):
    def __getattr__(self, item):
        item = item.upper()
        return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        key = key.upper()
        object.__setattr__(self, key, value)

    @staticmethod
    def getInstance(project):
        pro = Project()
        workbook = open_workbook('%s/config/MTK_Patch_mergepatch.xls' % scriptdir)
        worksheet = workbook.sheet_by_name('Sheet1')
        val = ['pmsProject', 'dint', 'spm', 'ccto']
        keys = worksheet.row_values(0)
	print '---keys---%s' %keys
        projects = worksheet.col_values(0, 1)
	print '---projects--%s' %projects
	#exit(1)
        values = None
        for i in xrange(projects.__len__()):
            if projects[i].lower() == project.lower():
                values = worksheet.row_values(i + 1)
		print '---values---%s' %values
		#exit(1)
                break
        if values:
            for i in xrange(keys.__len__()):
                if values[i] != '' and keys[i]:
		    print 'tttttttt'
                    if keys[i][:-1].lower() == 'pmsmap':
                        # pmsproject;dint;
                        v = values[i].strip().split(';')
                        s = {}
                        for j in xrange(val.__len__()):
                            try:
                                s[val[j]] = v[j].strip().split(',')
				print '---s[val[j]]---%s' %s[val[j]]
                            except Exception:
                                s[val[j]] = ''
                        if not hasattr(pro, 'pmsmap'):
                            pro.pmsMap = {}
			print s
			print '--------'
                        pro.pmsMap[v[0]] = s
			print '---pro.pmsMap---%s' %pro.pmsMap
			
                    else:
			print 'come here...'
                        print keys[i], values[i]
                        if isinstance(values[i], (str, unicode)):
                            setattr(pro, keys[i].upper(), values[i].strip())
                            # exec 'pro.%s = values[i].strip()' % (keys[i].upper())
                        else:
                            setattr(pro, keys[i].upper(), values[i])
                            # exec 'pro.%s = values[i]' % (keys[i].upper())
            pro.curpatchno = int(pro.curpatchno)
	    print 'pro.curpatchno---%s' %pro.curpatchno

            pro.modemcurno = int(pro.modemcurno)
            print 'pro.modemcurno---%s' %pro.modemcurno
            pro.import_dir = '/local/build/MTK_Patch/MTK_Patch_merge/%s_import' % project
            pro.patch_dir = '/local/build/MTK_Patch/MTK_Patch_merge/%s_patch' % project

            worksheet = workbook.sheet_by_name('modem_config')
            pro.modem_param = {}
            print '-----------------------', project in worksheet.col_values(0), project, worksheet.col_values(0)
	    #exit(1)
            if project in worksheet.col_values(0):
                modem_params = worksheet.row_values(worksheet.col_values(0).index(project), 1)
                print modem_params
                for i in xrange(0, modem_params.__len__(), 3):
                    if modem_params[i] and modem_params[i + 1] and str(modem_params[i + 2]):
                        pro.modem_param[modem_params[i].strip()] = [modem_params[i + 1].strip(), int(modem_params[i + 2].strip())]
            return pro
        else:
            print 'you should config %s/config/MTK_Patch_mergepatch.xls first' % os.path.dirname(
                os.path.abspath(__file__))
            raise Exception('try edit config file')


def getSpecial(branchname):
    branchfile = '%s/%s.xml' % (os.getcwd(), branchname)
    if os.path.exists(branchfile):
        result = {}
        for line in open(branchfile).readlines():
            match = re.search(r'<project name="(.*?)" path="(.*?)" revision="(.*?)"/>', line)
            if match:
                result[match.group(2)] = [match.group(3), match.group(1)]
        return result
    else:
        print branchname
        print '%s not exist' % (branchfile, branchname)
        return None


def getSpecials(project):
    if hasattr(project, 'pmsMap'):
        if not os.path.exists('%s/config/manifest' % scriptdir):
            docmd('rm -fr %s/config/manifest' % scriptdir)
            pushDir('%s/config' % scriptdir)
            docmd('git clone git@10.92.32.10:alps/manifest')
            pushDir('%s/config/manifest' % scriptdir)
        else:
            pushDir('%s/config/manifest' % scriptdir)
            docmd('git pull')
        result = {}
        for proj, val in project.pmsMap.iteritems():
            for dint in val['dint']:
                result[dint] = getSpecial(dint)
        for key in result.keys():
            if not result[key]:
                result.pop(key)
        popDir()
        return result


def copyPatch(project):
    cmd = 'scp -r {0}:{1}/{2}/* {3}/'.format(project.copyFrom, project.localPath, project.project, project.patch_dir)
    while True:
        print 'will docmd: %s' % cmd
        if getConf('Do you this this command is correct?<Y|N>').lower() == 'n':
            cmd = 'scp -r %s %s/' % (getConf(
                'please give the patch pathon your own computer.like\'user@10.92.32.132:/local/sdb/patch/pixi3-45-4g/*\''),
                                     project.import_dir)
            tmp = cmd.split(' ')[2].split(':')
            project.copyFrom = tmp[0]
            project.localPath = tmp[1]
        else:
            break
    while True:
        print 'the default password is : %s' % project.sshPassw
        if getConf('Do you this this password is correct?<Y|N>').lower() == 'n':
            project.sshPassw = getConf('please give your computer\'s password:', echo=False)
        else:
            break
    exp = {'%s\'s password:' % project.copyFrom: project.sshPassw,
           'Are you sure you want to continue connecting (yes/no)?': 'yes'}

    docmd('ssh {0} "rm {1}/{2}/*Zone.Identifier"'.format(project.copyFrom, project.localPath, project.project), exp=exp, exit=False)
    docmd(cmd, exp=exp, exit=False)
    ##zxq close docmd('ssh {0} "rm {1}/{2}/*.tar.gz"'.format(project.copyFrom, project.localPath, project.project), exp=exp, exit=False)


def envClean(project):
    pushDir(project.import_dir)
    print '--------sissy---begin to repo sync'
    docmd('repo forall -c "git checkout %s"' % project.Import)
    docmd('repo forall -c "pwd;git clean -df ;git reset --hard HEAD"')
    docmd('repo sync')
    popDir()


def getNextPatch(project):
    print "ls *%s.P%s*tar.gz" % (project.MPRelease, project.curPatchNo + 1)
    lines = commands.getoutput("ls *%s*P%s*.tar.gz" % (project.MPRelease, project.curPatchNo + 1))
    if lines:
        for line in lines.split('\n'):
            if os.path.isfile(line):
                print 'aaaaaaaaaaaaaaaaaaaaaaaaaa', line
                return line
    if project.modem_param:
        for key, value in project.modem_param.iteritems():
            if value[1] <= project.modemCurNo:
                print "ls *P%s*.tar.gz | grep '%s'" % (project.modem_param[key][1] + 1, key)
                lines = commands.getoutput("ls *P%s*.tar.gz | grep '%s'" % (project.modem_param[key][1] + 1, key))
                print lines
                if lines:
                    for line in lines.split('\n'):
                        print os.path.isfile(line), line
                        if os.path.isfile(line) and re.search('[\.-_]P%s\)?\.tar\.gz' % (project.modem_param[key][1] + 1), line):
                            return line
        return None
    else:
        print "ls *%s.P%s*.tar.gz" % (project.ModemVersion, project.modemCurNo + 1)
        lines = commands.getoutput("ls *%s.P%s*.tar.gz" % (project.ModemVersion, project.modemCurNo + 1))
        if not lines:
            return None
        else:
            for line in lines.split('\n'):
                if os.path.isfile(line) and re.search('[\.-_]P%s\)?\.tar\.gz' % (project.modemCurNo + 1), line):
                     return line


def untar(patch, project):
    if patch.type == 'modem':
        untar_dir = ''
        if project.modem_param:
            for key, value in project.modem_param.iteritems():
                print '--------------------------------'
                print patch.name, key
                if patch.name.__contains__(key):
                    untar_dir = value[0]
        else:
            untar_dir = 'modem'
        if not untar_dir:
            raise Exception('modem config error!')
        else:
            print 'untar modem to', untar_dir
        docmd('rm -fr %s' % patch.name_pms)
        docmd('mkdir -p %s/%s' % (patch.name_pms, untar_dir))
        print 'tar -xzvf %s -C %s/%s' % (patch.name_cmd, patch.name_P, untar_dir)
        docmd('tar -xzvf %s -C %s/%s' % (patch.name_cmd, patch.name_P, untar_dir))
        docmd('mv {0}/{1}/PatchList.txt {0}/'.format(patch.name_P, untar_dir))
    else:
        docmd('tar -xzvf %s' % patch.name_cmd)
        docmd('rm -rf %s' % patch.name_P)
        docmd('mv ./alps %s' % patch.name_P)
        print re.sub(r'\\', '', re.sub(r'\.tar\.gz', '.txt', patch.name_cmd))
        if os.path.exists(re.sub(r'\\', '', re.sub(r'\.tar\.gz', '.txt', patch.name_cmd))):
            docmd('mv {0} {1}/'.format(re.sub(r'\.tar\.gz', '.txt', patch.name_cmd), patch.name_P))
        else:
            docmd('mv patch_list.txt {0}/{1}'.format(patch.name_P, re.sub(r'\.tar\.gz', '.txt', patch.name_cmd)))


def scanList(gFolder, gitList, project):
    for g in commands.getoutput('ls %s' % gFolder).split('\n'):
        gtmp = gFolder + '/' + g
        print '****************%s' % gtmp
        if os.path.isdir(gtmp):
            if project.gitList.count(gtmp) == 1:
                gitList.append(gtmp)
            else:
                scanList(gtmp, gitList, project)


def getgitList(project, patch):
    gitList = []
    print '%s -> %s/%s' % (os.getcwd(), project.patch_dir, patch.name_P)
    os.chdir('%s/%s' % (project.patch_dir, patch.name_P))
    plist = commands.getoutput('ls').split('\n')
    print 'ls ->', plist
    for p in plist:
        print "*******%s" % p
        if os.path.isdir(p):
            print project.gitList.count(p)
            if project.gitList.count(p) == 1:
                gitList.append(p)
            else:
                scanList(p, gitList, project)
    patch.gitList = gitList
    return gitList


def Is_Need_To_Alarm(project):
    print "Is_Need_To_Alarm start"
    print project.patch_dir
    pushDir(project.patch_dir)
    if commands.getoutput('find . -name libnvram.so') or commands.getoutput('find . -name libnvram_sec.so'):
        Need_To_Alarm = True
    else:
        Need_To_Alarm = False
    print "Is_Need_To_Alarm end"
    popDir()
    return Need_To_Alarm


def mergePatch(patch, project):
    emailLink = {}
    pushDir(project.import_dir)
    change_files = [x for x in os.listdir('%s/%s' % (project.patch_dir, patch.name_P)) if x.endswith('.txt')]
    print change_files
    if not change_files: exit(1)
    change_git = getgitList(project, patch)
    if change_files:
        pushDir(project.import_dir)
        for change_file in change_files:
            content = open(os.path.join(project.patch_dir, patch.name_P, change_file)).read()
            delete_files = re.findall('delete\s+(.*?)\n', content)
            for delete_file in delete_files:
                if os.path.exists(delete_file):
                    print  'rm -fr %s' % delete_file
                    os.system('rm -fr %s' % delete_file)
                    delete_file_tmp = delete_file.split('/')
                    for i in xrange(len(delete_file_tmp)):
                        git_tmp = '/'.join(delete_file_tmp[:i+1])
                        if git_tmp in project.gitList:
                            if git_tmp not in change_git:
                                change_git.append(git_tmp)
                            break

    pushDir(project.import_dir)
    print os.getcwd()
    print 'cp -dpRv %s/%s/* .' % (project.patch_dir, patch.name_P)
    os.system('cp -dpRv %s/%s/* .' % (project.patch_dir, patch.name_P))
    currlists = commands.getoutput("repo forall -c 'git status --porcelain'|awk '{print$2}'").split('\n')
    normalfiles = ('.mk', '.c', '.java', '.xml', '.plf', '.cpp', '.h', '.sh', '.py')
    print "_____________________________________"
    print currlists
    print "_____________________________________"
    if currlists[0] == '':
        print 'no file changed,go to next package'
    else:
        for f in currlists:
            if not f.endswith(normalfiles):
                print '[kind notice] have binary files, go on!!\n'


    for git in change_git:
        pushDir('%s/%s' % (project.import_dir, git))
        os.system('git add .')
        comment = "porting %s" % patch.name_P
        os.system('git commit -am "porting %s"' % patch.name_P)

        print '---------------------\ngit push'
        #os.system('git push')
        git_clone = commands.getstatusoutput("git remote -v | grep push | awk '{ print $2 }'")
        match = re.search(r'/(mtk.*?)/(.*?\.git)', git_clone[1])
        if match:
            link = "http://10.92.32.10/sdd2/gitweb-%s/?p=%s;a=commit;h=" % (match.group(1), match.group(2))
        else:
            link = "http://10.92.32.10/sdd2/gitweb-%s/?p=%s.git;a=commit;h=" % (project.platform, git)
        outputcomment = commands.getoutput("git log -1")
        if outputcomment.find(comment) >= 0:
            commitId = outputcomment[7:47]
            link += commitId
            emailLink[git] = link
        popDir()
    popDir()
    return emailLink


def sendMail(project, patch, emailLink):
    Need_To_Alarm = Is_Need_To_Alarm(project)
    html = []
    html.append(
        u'<p align=\'Left\'><b>Dear %s,</b><br/></p>' % ' & '.join(
            [re.sub(r'(\.hz)?@tcl\.com', '', x) for x in patch.owner.split(',')]))
    html.append(u'<br>')
    html.append(
        u'<p align=\'Left\'>The patch:%s, which  is you applied, already merged to import branch.<br/></p>' % patch.name_P)
    html.append(
        u'<p align=\'Left\'>Please help to merge the patch to dint branch</b>and feedback to us the defect id!!<br/></p>')
    if project.specials:
        specialGit = {}
        for branch, val in project.specials.iteritems():
            tmp = [x for x in patch.gitList if x in val]
            if tmp:
                specialGit[branch] = tmp
        if specialGit:
            gitlist = []
            for val in specialGit.itervalues():
                gitlist.extend(val)
            gitlist = set(gitlist)
            for git in gitlist:
                if git in patch.gitList:
                    patch.gitList.pop(patch.gitList.index(git))
                    branchs = []
                    for branch, val in specialGit.iteritems():
                        if git in val:
                            branchs.append(project.specials[branch][git][0])
                        else:
                            branchs.append(branch)
                    html.append(u'<p align=\'Left\'>%s : %s<br/></p>' % (git, ', '.join(set(branchs))))
            if patch.gitList:
                html.append(u'<p align=\'Left\'>others : %s<br/></p>' % ', '.join(
                    reduce(lambda x, y: x + y, [x['dint'] for x in project.pmsMap.itervalues()])))

        else:
            html.append(u'<p align=\'Left\'>dint branch: %s<br/></p>' % ', '.join(
                reduce(lambda x, y: x + y, [x['dint'] for x in project.pmsMap.itervalues()])))
    else:
        html.append(
            u'<p align=\'Left\'>dint branch: %s<br/></p>' % ', '.join(
                reduce(lambda x, y: x + y, [x['dint'] for x in project.pmsMap.itervalues()])))
    html.append(u'<br>')
    #if Need_To_Alarm:
    #    html.append(u'<p align=\'Left\'><b>Dear qicai,</b><br/></p>')
    #    html.append(
    #        u'<p align=\'Left\'>Patch file include libnvram.so or libnvram_sec.so ,please apply the code from MTK</b></font><br/></p>')
    tmp = u'<p align=\'Left\'>Patch file already put to share server : \\\\10.92.32.12\\RDhzKM\\SWD-Share\\INT\\MTKPatch\\%s</b></font><br/></p>' % project.project
    html.append(tmp)
    html.append(
        u'<p align=\'Left\'>Please kindly give a feedback in 24h.When commit MTK related patch, please follow below comment:</b></font><br/></p>')
    html.append(u'<p align=\'Left\'><b>The comment same as: porting %s<br/></b></font></p>' % patch.name_P)
    html.append(u'<br>')
    html.append(u'<br>')
    html.append(u'<p align=\'Left\'>Import branch Link:</b><br/></p>')
    count = 0
    for git, url in emailLink.iteritems():
        count += 1
        html.append(u'<p align=\'Left\'>%d, %s:</b></p>' % (count, git))
        html.append(u'<p align=\'Left\'><a href="%s">%s</a></p>' % (url, url))
    html.append(u'<br>')
    html.append(u'<p align=\'Left\'>Best Regards</b></p>')
    html.append(u'<p align=\'Left\'>Integration Team</b></p>')

    sendtolist = []

    msg = MIMEMultipart('mixed')
    msg['Date'] = strftime("%a, %d %b %Y %T", localtime()) + ' +0800'
    msg['Subject'] = "%sPlatform [%s]: %s Patch Merge %s" % (
        project.platform[3:], project.project, project.project, patch.name_P)
    msg['From'] = project.email
    sendtolist.extend(patch.owner.split(','))

    #zxqccto = ['<shuzhong.cui.hz@tcl.com>', '<yu.he.hz@tcl.com>', '<ying.chen.hz@tcl.com>']
    #ccto = ['<shie.zhao@tcl.com>', '<yan.xiong@tcl.com>', '<xueqin.zhang@tcl.com>']
    ccto = ['<shie.zhao@tcl.com>']
    cc = filter(lambda x: x, [x['ccto'] for x in project.pmsMap.itervalues()])
    if cc:
        ccto.extend(cc)
    sendtolist.extend(ccto)
    for cc in ccto:
        if isinstance(cc, list):
            for c in cc:
                msg['Cc'] = c
        else:
            msg['Cc'] = cc

    #if Need_To_Alarm == True:
    #    msg['Cc'] = '<qicai.gu.hz@tcl.com>'
    #    sendtolist.append('<qicai.gu.hz@tcl.com>')
    #    #msg['Cc'] = '<guangming.yang.hz@tcl.com>'
    #    #sendtolist.append('<guangming.yang.hz@tcl.com>')

    for email in patch.owner.split(','):
        msg['To'] = email
        sendtolist.append(email)

    contMsg = MIMEMultipart('related')
    htmlPart = MIMEBase('text', 'html', charset="utf-8")
    htmlPart.set_payload(u'\n'.join(html).encode('utf-8'))
    encoders.encode_base64(htmlPart)
    contMsg.attach(htmlPart)
    msg.attach(contMsg)
    #zxqsendtolist = ['ying.chen.hz@tcl.com', 'yu.he.hz@tcl.com']
    sendtolist = ['shie.zhao@tcl.com']
    s = smtplib.SMTP('mailsz.tct.tcl.com')
    s.login(project.username, project.password)
    s.set_debuglevel(0)
    #zxqs.sendmail(project.email, 'ying.chen.hz@tcl.com', msg.as_string())
    s.sendmail(project.email, 'shie.zhao@tcl.com', msg.as_string())
    #s.sendmail(project.email, 'yu.he.hz@tcl.com', msg.as_string())
    print '===================', project.email
    #s.sendmail(project.email, sendtolist, msg.as_string())
    print "---send mail ok--------"
    s.quit()


def getEserviceFromTxt(project, patch):
    pushDir('%s/%s' % (project.patch_dir, patch.name_P))
    txts = commands.getoutput('ls | grep txt').split('\n')
    for txt in txts:
        if txt == 'PatchList.txt' or txt.find(re.sub(r'\.tar\.gz', '.txt', patch.name)) != -1:
            msg = []
            for line in open(txt).readlines():
                # print line
                match = re.search(r'CR ID:\s+(MOLY\d+)|\s+(ALPS\d+)', line)
                if match:
                    msg.append(match.group(1) if patch.type == 'modem' else match.group(2))
            if msg:
                print msg
                return 'Apply Patch: %s' % ', '.join([x for x in msg if x])

        else:
            continue
    print 'couldn\'t get eservice msg!!'
    return 'Apply Patch:'

def getProjectId(projectName):
    projectName = re.sub(r'SW\.|QA\.|[\._\- ]', '', projectName).lower()
    for item in json.loads(urllib2.urlopen('http://10.92.35.176/pmsapi/common/commonlist/project/list').read())['data']:
        project = re.sub(r'SW\.|QA\.|[\._\- ]', '', item['projectName'])
        if project.lower() == projectName:
            return item['autoId']


def sendPMS(project, patch):
    url = 'http://10.92.35.176/pms/project/mtk-patch/0/saveForInfoJson?jsonContent='
    # url = 'http://10.92.33.42:8080/pms/project/mtk-patch/0/saveForInfoJson?jsonContent='
    rows = {}
    rows['eservice'] = str(patch.eservice)
    rows['patchName'] = urllib.quote(str(patch.name_P))
    rows['summary'] = urllib.unquote(str(getEserviceFromTxt(project, patch)))
    rows['ownerEmail'] = ''
    rows['affectedGit'] = ''
    rows['comment'] = ''
    rows['projectId'] = ''
    rows['branch'] = ''
    flag = None
    ddd = []
    for projectName, val in project.pmsMap.iteritems():
        print val
        rows['projectId'] = urllib.quote(str(val['pmsProject'][0]))
        rows['ownerEmail'] = urllib.quote(str(patch.owner)) if patch.owner.split(',').__len__() == 1 else urllib.quote(
            str(val['spm'][0]))
        if patch.type == 'modem':
            rows['branch'] = [str(project.Import)]
            for branch in val['dint']:
                if branch in project.specials and 'modem' in project.specials[branch]:
                    rows['branch'].append(str(project.specials[branch]['modem'][0]))
                else:
                    rows['branch'].append(str(branch))
        elif val['dint']:
            rows['branch'] = [str(project.Import), str(','.join(val['dint']))]
        print rows
        ddd.append(deepcopy(rows))
        msg = []
        for key, values in rows.iteritems():
            if key in ['comment', 'summary']:
                if values.__contains__("'"):
                    form = '"%s":"%s"'
                else:
                    form = "'%s':'%s'"
                msg.append(form % (key, urllib.quote(values)))
            elif isinstance(values, list):
                mmsg = '"%s":[' % key
                for val in values:
                    mmsg += '"%s",' % val
                mmsg = mmsg[:-1] + ']'

                msg.append(mmsg)
            else:
                msg.append('"%s":"%s"' % (key, values))
        msg = '{%s}' % ','.join(msg)
        print url + msg
        try:
            data = urllib2.urlopen(url + msg).read()
            print data
        except Exception, e:
            flag = e
            print e
    if flag:
        savedatatoxls(project, ddd)
        print flag

def savedatatoxls(project, ddd):
    xlspath = os.path.dirname(scriptdir) + '/' + project.project + '.xls'
    if os.path.exists(xlspath):
        w = open_workbook(xlspath)
        index = w.sheet_names().index(project.project)
        row = w.sheet_by_name(project.project).nrows
        wb = copy(w)
        sheet = wb.get_sheet(index)
    else:
        wb = Workbook()
        sheet = wb.add_sheet(project.project)
        sheet.write(0, 0, 'ProjectID')
        sheet.write(0, 1, 'Patch')
        sheet.write(0, 2, 'Owner')
        sheet.write(0, 3, 'Eservice')
        sheet.write(0, 4, 'Comment')
        sheet.write(0, 5, 'Summary')
        sheet.write(0, 6, 'Branch')
        sheet.write(0, 7, 'Status')
        sheet.write(0, 8, 'Bug ID')
        sheet.write(0, 9, 'Resolved time')
        sheet.write(0, 10, 'Verified SW time')
        row = 1
    print ddd
    for rows in ddd:
        print rows
        for branch in rows['branch']:
            sheet.write(row, 0, rows['projectId'])
            sheet.write(row, 1, rows['patchName'])
            sheet.write(row, 2, rows['ownerEmail'])
            sheet.write(row, 3, rows['eservice'])
            sheet.write(row, 4, ' ')
            sheet.write(row, 5, rows['summary'])
            sheet.write(row, 6, branch)
            sheet.write(row, 7, 'merged' if branch.find('import') > -1 else 'merge')
            sheet.write(row, 8, ' ')
            sheet.write(row, 9, ' ')
            sheet.write(row, 10, ' ')
            row += 1
        row += 2
    wb.save(xlspath)

def writeToxls(project):
    global __file__
    if lock.acquire():
        wb = open_workbook('%s/config/MTK_Patch_mergepatch.xls' % scriptdir)
        worksheet = wb.sheet_by_name('Sheet1')
        workbook = Workbook()
        sheet = workbook.add_sheet('Sheet1')
        for i in xrange(worksheet._cell_values.__len__()):
            if worksheet._cell_values[i][0] == project.project:
                for j in xrange(worksheet._cell_values[i].__len__()):
                    if j == 9:
                        sheet.write(i, j, str(project.curPatchNo))
                    elif j == 10:
                        sheet.write(i, j, str(project.modemCurNo))
                    else:
                        sheet.write(i, j, worksheet._cell_values[i][j])
            else:
                for j in xrange(worksheet._cell_values[i].__len__()):
                    sheet.write(i, j, worksheet._cell_values[i][j])
        worksheet = wb.sheet_by_name('modem_config')
        sheet2 = workbook.add_sheet('modem_config')
        for i in xrange(worksheet._cell_values.__len__()):
            if worksheet._cell_values[i][0] == project.project:
                for j in xrange(worksheet._cell_values[i].__len__()):
                    if j!= 0 and j % 3 == 0:
                        if worksheet._cell_values[i][j-2].strip():
                            sheet2.write(i, j, str(project.modem_param[worksheet._cell_values[i][j-2].strip()][1]))
                        else:
                            sheet2.write(i, j, worksheet._cell_values[i][j])
                    else:
                        sheet2.write(i, j, worksheet._cell_values[i][j])
            else:
                for j in xrange(worksheet._cell_values[i].__len__()):
                    sheet2.write(i, j, worksheet._cell_values[i][j])
        workbook.save('%s/config/MTK_Patch_mergepatch.xls' % scriptdir)
        lock.release()


def main(project):
    project = Project.getInstance(project)
    project.specials = getSpecials(project)
    copyPatch(project)
    envClean(project)
    project.gitList = open('%s/.repo/project.list' % project.import_dir).read().split('\n')
    try:
        while True:
            if hasattr(project, 'modem_param'):
                print project.modem_param
            pushDir(project.patch_dir)
            patch = getNextPatch(project)
            print 'new patch:',patch
            if patch:
                patch = Patch.getInstance(patch, project)
                print '[kind notice] find new patch need to merge: %s' % patch.name
                untar(patch, project)
                popDir()
                emailLink = mergePatch(patch, project)
                print '%s \t%s' % (project.project, patch.name)
                print type(reduce(lambda x, y: x + y, [x['spm'] for x in project.pmsMap.itervalues()]))
                patch.owner = getConf('please input the reciever, if is spm, please just press enter',
                                      val=','.join(
                                          reduce(lambda x, y: x + y, [x['spm'] for x in project.pmsMap.itervalues()])))
                sendMail(project, patch, emailLink)
                print '++++++++++++++++++++++++++++++++++'
                if patch.type == 'modem':
                    if project.modem_param:
                        for key, value in project.modem_param.iteritems():
                            if patch.name.__contains__(key):
                                print 'set', key, project.modem_param[key][1], ' + 1'
                                project.modem_param[key][1] += 1
                                break
                        list_tmp = [x[1] for x in project.modem_param.values()]
                        if min(list_tmp) == max(list_tmp):
                            print project.modemCurNo
                            project.modemCurNo = max(list_tmp)
                            print project.modemCurNo
                    else:
                        print project.modemCurNo
                        project.modemCurNo += 1
                        print project.modemCurNo
                else:
                    print project.curPatchNo
                    project.curPatchNo += 1
                    print project.curPatchNo
                print '++++++++++++++++++++++++++++++++++'
                sendPMS(project, patch)

            else:
                break
    finally:
        writeToxls(project)



lock = threading.Lock()
if __name__ == '__main__':
    global scriptdir
    scriptdir = os.path.dirname(os.path.abspath(__file__))
    # threadQue = {}
    project = getConf('please enter the project name you want to merge. or no')
    main(project)
    #th = threading.Thread(target=main, args=(project,))
    #th.daemon = True
    #threadQue[project] = th
    #for pro, th in threadQue.iteritems():
    #    print 'start', pro
    #    th.start()
    #    th.join()





