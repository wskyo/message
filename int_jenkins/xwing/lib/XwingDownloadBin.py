#!/usr/bin/env python
# -*- coding: utf-8 -*-

############################################################################
## XwingDownloadBin.py be user to download daily/appli for 2 phones automatically.
## add by xueqin.zhang for xwing create 2015-05-20
## if teleweb.exe/adb.exe exist,auto killed first;when phone1 download end sleep 500. update by xueqin.zhang  2015-05-27
############################################################################

from pywinauto import application
import time
import os
import sys
import glob
import re

#python c:\XwingDownloadBin.py pixi3-45 6D25-4 0 3.5.1
#python c:\XwingDownloadBin.py pixi3-45 6D25 ZZ 3.5.1
def main():
    if len(sys.argv) != 5:
        print '%s need 4 parameter!' % sys.argv[0]
        sys.exit(1)
    PROJECT = sys.argv[1]
    VERSION = sys.argv[2]
    PERSO = sys.argv[3]
    TELEVERSION = sys.argv[4]

    os.chdir('C:\\Program Files\\TeleWeb MTK_SP %s' % TELEVERSION)
    f=open('TeleWeb.ini','r+')
    str_replace = re.sub(r'ServerLoc=0', 'ServerLoc=2',f.read())
    f1=open('file1.ini', 'w')
    f1.write(str_replace)
    f.close()
    f1.close()

    f=open('file1.ini','r+')
    str_replace = re.sub(r'Poweron=0', 'Poweron=1',f.read())
    f2=open('file2.ini', 'w')
    f2.write(str_replace)
    f.close()
    f2.close()

    f=open('file2.ini','r+')
    str_replace = re.sub(r'LiveUpdateOn=1', 'LiveUpdateOn=0',f.read())
    f3=open('TeleWeb.ini', 'w')
    f3.write(str_replace)
    f.close()
    f3.close()
    
    if len(sys.argv[2]) == 6:
        CLASSIFY = "Daily_version"
        TELEWEBIMG = "http://10.92.32.20/SECURITY/LIVRAISON_BF/0_Huizhou/Android_SP/%s/%s/v%s/" % (PROJECT, CLASSIFY, VERSION)

    if len(sys.argv[2]) == 4:
        CLASSIFY = "appli"
        TELEWEBIMG = "http://10.92.32.20/SECURITY/LIVRAISON_BF/0_Huizhou/Android_SP/%s/%s/v%s/" % (PROJECT, CLASSIFY, VERSION)
        TELEWEBSECIMG = "http://10.92.32.20/SECURITY/LIVRAISON_BF/0_Huizhou/Android_SP/%s/perso/%s/%s" % (PROJECT, VERSION, PERSO)
    
    os.chdir('c:\\')
    os.system('rmdir /s /q teleweb_image')
    os.system('md teleweb_image')
    os.chdir('teleweb_image')
    os.system('wget -r -nd -np --no-proxy -l1 --reject=index* --reject=*.zip --http-user=hznpi1 --http-passwd=jVNvC234  %s' % TELEWEBIMG)
    if PERSO != "0":
        os.system('wget -r -nd -np --no-proxy -l1 --reject=index* --reject=*.zip --http-user=hznpi1 --http-passwd=jVNvC234  %s' % TELEWEBSECIMG)

    scatterFile = glob.glob('K*')[0]
    print scatterFile

    os.system('taskkill /im TeleWeb.exe /f /im adb.exe')
    
    print 'Start download...'
    app = application.Application()
    app.start_("C:\Program Files\TeleWeb MTK_SP %s\TeleWeb.exe" % TELEVERSION)
    app.TelewebS.Edit1.SetText('hong.ran')
    app.TelewebS.Edit2.SetText('BeGEf436')
    app.TelewebS.Button1.Click()
    time.sleep(3)
    app.connect_(title_re='TeleWeb MTK_SP.*')
    dlg = app.window_(title_re='TeleWeb MTK_SP.*')
    if dlg.CheckBox1.GetCheckState() == 1:
        dlg.CheckBox1.Click()
    if PROJECT == "pixi3-4":
        PROJECTLIST = "Pixi3-4"
    elif PROJECT == "twin":
        PROJECTLIST = "Twin"
    elif PROJECT == "pixi3-45":
        PROJECTLIST = "Pixi3-4.5"
    elif PROJECT == "pixi3-5_3g":
        PROJECTLIST = "Pixi3-5 3G"
    elif PROJECT == "pixi3-55_3g":
        PROJECTLIST = "Pixi3-5.5 3G"
    dlg.ComboBox2.Select(PROJECTLIST)

    time.sleep(3)
    dlg['...'].Click()
    time.sleep(3)
    opendlg = app.top_window_()
    opendlg.Edit.SetText('c:\\teleweb_image\\%s' % scatterFile)
    time.sleep(5)
    opendlg.Button1.Click()
    time.sleep(10)
    
    dlg['Download'].Wait('enabled', timeout=600)
    dlg['Download'].Click()

    os.system('adb devices')
    
    p1=os.popen('adb devices | sed -n 2p | awk "{print $1}" ')
    DEVICE1=p1.read().strip("\n")
    print DEVICE1
    p1.close()

    p2=os.popen('adb devices | sed -n 3p | awk "{print $1}" ')
    DEVICE2=p2.read().strip("\n")
    print DEVICE2
    p2.close()
    
    os.system('adb -s %s reboot' % DEVICE1)

    resdlg=app.window_(title='TeleWeb')
    resdlg.Wait('enabled',timeout=3600)
    time.sleep(10)
    resdlg.Button1.Click()
    print 'Complete download phone1...'
    
    time.sleep(500)
    
    print 'Begin download phone2...'
    dlg['Download'].Wait('enabled', timeout=600)
    dlg['Download'].Click()
    os.system('adb -s %s reboot' % DEVICE2)
    resdlg=app.window_(title='TeleWeb')
    resdlg.Wait('enabled',timeout=3600)
    time.sleep(10)
    resdlg.Button1.Click()
    app.Kill_()
    print 'Complete download phone2...'

if __name__ == '__main__':
    main()
