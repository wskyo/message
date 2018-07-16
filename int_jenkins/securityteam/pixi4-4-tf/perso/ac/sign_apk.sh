#!/bin/bash
# Script to sign apk
#

echo "Start sign!"
date

sign_place="perso"; 
sign_project="$1";
sign_key="TF_0222";
sign_log="$1-perso";
builddir=$3
mtk_project="$2";
combin=$4

cur_date=`date +%y%m%d_%H%M%S`
log_file="$sign_log-$cur_date"
log_num=0;
new_log_file=$log_file


touch $new_log_file.log

#cd $sign_project
function cleanBuild
{
  cd ../../build
  git reset --hard HEAD && git clean
  cd -
}

function copySignFile
{
    echo "cp -r ac to $builddir"  >>$builddir/$new_log_file.log
    cp -f /local/int_jenkins/securityteam/$sign_project/perso $builddir

    chmod -R a+x perso
}

function copyKeyFile
{
    echo "begin to copy TCL_ReleaseKeys.zip"  >>$builddir/$new_log_file.log
    cp -f /local/int_jenkins/securityteam/$sign_project/TCL_ReleaseKeys.zip ../../build/target/product/security/
    cd ../../build/target/product/security
    unzip -o TCL_ReleaseKeys.zip
    if [ $? -ne 0 ]; then
        echo "Fail to unzip  TCL_ReleaseKeys.zip "  >>$builddir/$new_log_file.log
        exit 1
    fi
    echo "Success to unzip  TCL_ReleaseKeys.zip "  >>$builddir/$new_log_file.log
    cd -
}


echo "begin to sign perso apk"  >>$builddir/$new_log_file.log
#copySignFile
#copyKeyFile


if [ $sign_place == 'perso' ];then
#by zs 20151111 start

	./releasekey.sh $sign_key $mtk_project $builddir >>$builddir/$new_log_file.log
	
	#rm -f releasekey.sh
	#rm -f signapk.sh
	#rm -f releasesign.sh
fi
echo "Sign perso finish!!" >>$builddir/$new_log_file.log
if [ $combin == 1 ];then 
  ./releasekeyForCombine.sh TF_0222 $mtk_project ./
  echo "releasekeyForCombine.sh finish!!" >>$builddir/$new_log_file.log
  perl ../../vendor/jrdcom/build/jrdmagic/jrd_magic.pl $mtk_project
else
  ./zipcustpackimg.sh $mtk_project
  echo "./zipcustpackimg.sh $mtk_project finish!"
fi
echo "umount system" >>$builddir/$new_log_file.log
./umount_system.sh $mtk_project tcl@3214

date
