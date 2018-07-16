#!/bin/bash

if [ ! -n "$1" ];then
   echo "Please input FTPpath ,Project and Version"
   read FTPpath Project version
else
   FTPpath=$1
   Project=$2
   version=$3
fi

ip='218.18.53.212'
username='TCL'
password='tcl!@#qazxsw'


telewebip='10.92.32.26'
telewebuser='sl_hz_hran'

echo "******begin to upload img to FTP****"
echo ${ip} ${username} ${password} ${version} ${Project} ${FTPpath}
version_dir="/local/release/${Project}-release/v${version}/"

if [[ ${version:2:1} =~ [U-Z] ]] ;then
  cu_mini_daily='mini'
elif [[ ${#version} -eq "6" ]] ;then
  cu_mini_daily='Daily_version'
else
  cu_mini_daily='appli'
fi
  echo ${cu_mini_daily}

telewebdir="/mfs/teleweb/${Project}/${cu_mini_daily}/v${version}"
persodir="/mfs/teleweb/${Project}/perso/${version}/*"

if [ -d ${version_dir} ] ;then
  echo ${version_dir}
else
  echo "**begin to download version from teleweb"
  echo ${telewebdir}
  scp -r -o StrictHostKeyChecking=no ${telewebuser}@${telewebip}:${telewebdir} /local/release/${Project}-release/
fi

if [ -d ${mtxgen_dir} ] && [[ ${version:2:1} =~ [U-Z] ]] ;then
cd ${version_dir}
tar -zcf  mtxgen.tar.gz mtxgen
fi

ftp -v -n ${ip} <<EOF
user TCL tcl!@#qazxsw
binary
hash
cd ${FTPpath}
pwd
mkdir v${version}
cd v${version}
lcd ${version_dir}
prompt
mput *
quit
EOF

if [ ${#version} -eq "4" ] && [[ ! ${version:2:1} =~ [U-Z] ]];then
cd ${version_dir}
if [ -d ${version_dir}/perso/ ] ;then
  cd perso
else   
  mkdir perso
  cd perso
  scp -r -o StrictHostKeyChecking=no ${telewebuser}@${telewebip}:${persodir} .
  perso_list=`ls` 
  for  personame  in ${perso_list}
     do    
        tar -zcf  ${personame}.tar.gz ${personame}
     done
fi
echo "********begin to upload perso********"
ftp -v -n ${ip} <<EOF
user TCL tcl!@#qazxsw
binary
hash
cd ${FTPpath}/v${version}
pwd
mkdir perso
cd perso
lcd ${version_dir}/perso/
prompt
mput *
quit
EOF
fi

echo "***********end to upload img to FTP********"

        
       


