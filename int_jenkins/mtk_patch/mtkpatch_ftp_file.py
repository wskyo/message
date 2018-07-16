#!/usr/bin/python
#
#for dowload mtk patch by using ftplib.py
#

from ftplib import FTP
import os
import commands

class myftp:
	#url:	"mft.mediatek.com"
	def __init__(self,url,user,passwd):
		#stab ftp to url
		self.ftp = FTP(url)
		print self.ftp
		#login
		print self.ftp.login(user,passwd)

	def chdir(self,ftp_dir):
		#change dir of ftp dir
		print 'chdir to %s'%ftp_dir	
		print self.ftp.cwd(ftp_dir)
	def ls(self):
		#return list file of pwd
		return self.ftp.nlst()
	def pwd(self):
		return self.ftp.pwd()
	def ftp_cp(self,ftp_file,filename,redownload=False):
		#like cp ftp_file filename
		#ftp_file :	file name on ftp 
		#filename :	local file name
		#r_v ==	1		: return 'ftp success!!!'
		#r_v ==	0		: return 'ftp fail!!!'
		#r_v == 2 or othner	: return 'file have exists'
		r_v = ''
		if not os.path.isfile(filename):
			print 'no such file,create it'
			commands.getoutput("touch '%s'" % filename)
			fn = open(filename,'wrb')
			ftp_rz = self.ftp.retrbinary('RETR '+'%s' % ftp_file,fn.write,1024)
			print 'ftp_rz====',ftp_rz
			fn.close()
			if ftp_rz.find('Closing data connection, Binary transfer complete.')!=-1:
				r_v = 1
			else:
				r_v = 0
		else:
			r_v = 2
		if redownload:
			print 're down load file'
			fn = open(filename,'wrb')
			ftp_rz = self.ftp.retrbinary('RETR '+'%s' % ftp_file,fn.write,1024)
			print 'ftp_rz====',ftp_rz
			fn.close()
			if ftp_rz.find('Closing data connection, Binary transfer complete.')!=-1:
				r_v = 1
			else:
				r_v = 0
		if r_v == 1:
			return 'ftp success!!!'
		elif r_v == 0:
			return 'ftp fail!!!'
		else:
			return 'file exist!!!'
		
	def close(self):
		self.ftp.close()

if __name__=='__main__':
	print 'start'
	print commands.getoutput("date")
	mtk = myftp("mft.mediatek.com","wei.deng@tcl.com","tcl@12345")
	mtk.chdir('Inbox/SDM')
	tmp_pl = mtk.ls()
	print tmp_pl
	today = commands.getoutput("date +'%Y-%m%d'")
	yesterday = commands.getoutput("date -d '1 day ago' +'%Y-%m%d'")
	bf_yesterday = commands.getoutput("date -d '2 day ago' +'%Y-%m%d'")
	print today,yesterday,bf_yesterday
	mtk_pl=[]
	for tmp_p in tmp_pl:
		if tmp_p.find(today)!=-1:
			mtk_pl.append(tmp_p)
		elif tmp_p.find(yesterday)!=-1:
			mtk_pl.append(tmp_p)
		#elif tmp_p.find(bf_yesterday)!=-1:
			#mtk_pl.append(tmp_p)
		else:
			continue
	print mtk_pl
	for mtk_p in mtk_pl:
		print mtk_p
		mtk.chdir(mtk_p)
		mtk_pf = mtk.ls()
		print mtk_pf
		if mtk_pf:
			mtk_nstp = mtk_pf[-1]
			print mtk_nstp
			tmp_st = mtk.ftp_cp(mtk_nstp,'/local/mtk_patch_import/TODO/'+mtk_nstp)
			if tmp_st=='ftp success!!!':
				print 'ftp success!!!'
				mtk.chdir('..')
				continue
			elif tmp_st=='file exist!!!':
				print 'file exist!!!'
				mtk.chdir('..')
				continue
			else:
				for n in [0,1,2]:
					tmp_st = mtk.ftp_cp(mtk_nstp,'/local/mtk_patch_import/TODO/'+mtk_nstp,True)
					if tmp_st=='ftp success!!!':
						print 'ftp success!!!'
						mtk.chdir('..')
						break
					if n==2:
						print '####try third times but fail.####'

	mtk.close()
	print commands.getoutput("date")
	print 'end'
#mtk=FTP("mft.mediatek.com")

#mtk.login("wei.deng@tcl.com","tcl@12345")
#mtk.pwd()#/
#mtk.cwd('Inbox/SDM')

#mtk.nlst()
#date +"%Y-%m%d"
#date -d "1 day ago" +"%Y-%m%d"
#date -d "2 day ago" +"%Y-%m%d"
#date +"%Y-%m-%d-%H"
#['2017-0330-0208-02000674', '2017-0330-1009-15000686', '2017-0330-1014-03000058', '2017-0330-1107-09000484', '2017-0330-1255-16000237', '2017-0330-1334-17000965', '2017-0330-1643-03000075', '2017-0330-1834-06000494', '2017-0330-1834-15000203', '2017-0330-2004-56000158', '2017-0330-2155-13000144', '2017-0331-0125-03000698', '2017-0331-0125-11000120', '2017-0331-1046-02000934', '2017-0331-1528-09000879', '2017-0331-1613-10000970', '2017-0331-1646-18000751', '2017-0331-2151-51000351', '2017-0401-0125-39000643', '2017-0401-0125-50000605', '2017-0401-1643-03000134', '2017-0405-1355-03000153', '2017-0405-1511-24000625', '2017-0405-1529-22000674', '2017-0405-1555-12000823', '2017-0405-1638-03000454', '2017-0405-2108-31000730', '2017-0406-0316-03000201', '2017-0406-0537-29000616', '2017-0406-0555-35000515', '2017-0406-0904-25000347', '2017-0406-1443-08000539', '2017-0406-1916-03000263', '2017-0406-2025-17000094', '2017-0407-0649-21000815', '2017-0407-0948-45000236', '2017-0407-1228-03000099', '2017-0407-1346-03000464', '2017-0407-1346-17000512', '2017-0407-1346-37000204', '2017-0407-1352-18000627', '2017-0407-1352-30000394', '2017-0407-1446-21000222', '2017-0409-1334-02000697', '2017-0410-1425-23000822', '2017-0410-1646-04000357', '2017-0410-1704-03000333', '2017-0410-2334-09000299', '2017-0411-2004-04000185']

#mtk.cwd('2017-0411-2004-04000185')
#os.system('touch ALPS03211324(For_jhz6737m_65_cd_n_alps-mp-n0.mp1-V1.0.2_P111).tar.gz')
#f=open('ALPS03211324(For_jhz6737m_65_cd_n_alps-mp-n0.mp1-V1.0.2_P111).tar.gz','wrb')
#mtk.retrbinary('RETR '+'ALPS03211324(For_jhz6737m_65_cd_n_alps-mp-n0.mp1-V1.0.2_P111).tar.gz',f.write,1024)
#mtk.close()
#user@shie-zhao5-swd1:~$ ping -c 5 mft.mediatek.com
#PING mft.mediatek.com (60.250.185.107) 56(84) bytes of data.
#64 bytes from 60-250-185-107.hinet-ip.hinet.net (60.250.185.107): icmp_req=1 ttl=242 time=102 ms
#64 bytes from 60-250-185-107.hinet-ip.hinet.net (60.250.185.107): icmp_req=2 ttl=242 time=34.6 ms
#64 bytes from 60-250-185-107.hinet-ip.hinet.net (60.250.185.107): icmp_req=3 ttl=242 time=34.7 ms
#64 bytes from 60-250-185-107.hinet-ip.hinet.net (60.250.185.107): icmp_req=4 ttl=242 time=34.4 ms
#64 bytes from 60-250-185-107.hinet-ip.hinet.net (60.250.185.107): icmp_req=5 ttl=242 time=33.9 ms

#--- mft.mediatek.com ping statistics ---
#5 packets transmitted, 5 received, 0% packet loss, time 4006ms
#rtt min/avg/max/mdev = 33.984/48.012/102.212/27.101 ms

