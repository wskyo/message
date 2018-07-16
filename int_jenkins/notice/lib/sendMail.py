#!/usr/bin/python
import os
import sys
import re
import common
import emailUtils
import time


def set_mail_info(addrs):
    to_list = []
    cc_list = [] 
    to_list_str = addrs
    #to_list_str = 'yinfang.lai@tcl.com'   
    cc_list_str = 'xiaoying.huang@tcl.com'
    domain = 'hudson.admin.hz'
    domain_passwd = 'Hzsw#123'
    name='hudson.admin.hz'
    mail='hudson.admin.hz@tcl.com'

    if to_list_str.strip():
        to_list = to_list_str.split(',')
    if cc_list_str.strip():
        cc_list = cc_list_str.split(':')
    subject = '[Patch Review List] ( %s ~ %s )'%(times[0],times[1])
    mail_content = mail_head_content(ResultPath)
    mail_content += mail_bottom_content()
    send_mail.send_mail(domain,mail, subject, mail_content, to_list,name,domain_passwd,cc_list,None,ResultPath)

def mail_head_content(ResultPath):
    html = '''<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <meta http-equiv="Content-Type" content="text/html;charset=gb2312"/>
    <style type="text/css">
    body {font-family:arial; font-size:10pt;}
    td {font-family:arial; font-size:10pt;}
    </style>
    <title>Patch Review List</title>
    </head>
    <body>
    <p>Dear All,</p>
    <pre>    This is the Statistics of Patch Review , Please find the data from : 
    http://10.92.35.20/data/Review_results/%s_%s
    If you find it is not correct ,please tell me ,thanks!</pre>
    ''' % (times[0], times[1])
    return html

def mail_bottom_content():
    html = '<br /> '
    html += '<p><font color="gray">'
    html += 'Best Regards,<br />'
    html += 'hudson.admin.hz' + '<br />'
    html += 'TEL: 0752-2639 227 <br />'
    html += 'MAIL: ' + 'hudson.admin.hz@tcl.com' + '<br />'
    html += 'ADDR: HZ Product Innovation Center SWD1 TCL COMMUNICATION TECHNOLOGY HOLDINGS LIMITED'+ \
            '70 Huifeng 4th,ZhongKai Hi-tech Development District,Huizhou,Guangdong 516006 P.R.China'
    html += '</font></p>'
    html += '</body>'
    html += '</html>'
    return html


if __name__ == '__main__':
	if len(sys.argv) <1 :
		sys.exit(0)
 	set_mail_info(sys.argv[1])
