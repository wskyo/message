#!/bin/bash

JOB_NAME=$1
baseversion=$2
blacksuffix=$3
band=$4
project=$5
combin=$6



relaseblackdir="/local/release/${JOB_NAME}/v${baseversion}-black-${blacksuffix}"
buildblackdir="/local/black/${JOB_NAME}/v${baseversion}-black-${blacksuffix}"

main=${baseversion:0:4}
if [ ${#baseversion} == "6" ]; then
    sub=${baseversion:5:1}
else
    sub=0
fi

if [ ${baseversion:3:1} == "X" ]; then
    perso=0
else 
    perso=${baseversion:3:1}
fi


if [ ! -d ${buildblackdir} ]; then ls $buildblackdir; echo "Please input correct build path.";exit; fi

if [ -z $4 ]; then
   echo -e "Use default Band:EU. You can change it.Refer to band mapping table below:\n\tEU:EU\n\tUS: U0\n\tUS1:U1\n\tUS2:U2\n\tAWS:AW"
   band="EU"
elif [ ${#4} == "2" ]; then
   band=$4
else
   echo -e "Band Error: please input right band info!Band refer to band mapping table below:\n\tEU:EU\n\tUS: U0\n\tUS1:U1\n\tUS2:U2\n\tAWS:AW"
fi


echo -e "builddir:$buildblackdir\nreleasedir:$relaseblackdir\nversion:$baseversion perso:$perso band:$band"

if [ ! -d ${relaseblackdir} ];then
	mkdir -vp ${relaseblackdir}
	mkdir -vp "${relaseblackdir}/flashtool"

fi

if [ ${JOB_NAME} == "pixi4-4-tf-black" ] && [ ${project} == "pixi4_4_tf" ];then
	echo $combin
	mv ${relaseblackdir}/flashtool/logo.bin ${relaseblackdir}/flashtool/logo_maincode.bin
	mv ${relaseblackdir}/flashtool/secro.img ${relaseblackdir}/flashtool/secro_maincode.img
	if [ $combin == "1" ];then
	  #mv ${relaseblackdir}/flashtool/system.img ${relaseblackdir}/flashtool/system_maincode.img
	  cp ${buildblackdir}/out/target/product/${project}/signed_bin/system-sign.img ${relaseblackdir}/flashtool
	fi

	cp ${buildblackdir}/out/target/product/${project}/signed_bin/logo-sign.bin ${relaseblackdir}/flashtool
	cp ${buildblackdir}/out/target/product/${project}/signed_bin/secro-sign.img ${relaseblackdir}/flashtool
else

	echo $combin
	mv ${relaseblackdir}/flashtool/logo.bin ${relaseblackdir}/flashtool/logo_maincode.bin
	mv ${relaseblackdir}/flashtool/secro.img ${relaseblackdir}/flashtool/secro_maincode.img
	if [ $combin == "1" ];then
	  mv ${relaseblackdir}/flashtool/system.img ${relaseblackdir}/flashtool/system_maincode.img
	  cp ${buildblackdir}/out/target/product/${project}/system.img ${relaseblackdir}/flashtool
	else
	  mv ${relaseblackdir}/flashtool/custpack.img ${relaseblackdir}/flashtool/custpack_maincode.img
	  cp ${buildblackdir}/out/target/product/${project}/custpack.img ${relaseblackdir}/flashtool
	fi

	cp ${buildblackdir}/out/target/product/${project}/logo.bin ${relaseblackdir}/flashtool
	cp ${buildblackdir}/out/target/product/${project}/secro.img ${relaseblackdir}/flashtool
fi

cd ${relaseblackdir}

case $band in
    "EU" )
        BN='EU';;
    "US" )
        BN='U0';;
    "US0" )
        BN='U0';;
    "CN" )
        BN='CN';;
    "LATAM2G" )
        BN='L2';;
    "LATAM3G" )
        BN='L3';;
    "AWS" )
        BN='AW';;
    "US1" )
        BN='U1';;
    "US2" )
        BN='U2';;
    * )
        echo "No such band! (EU|US0|US|US1|US2|AWS|LATAM2G|LATAM3G)"
        exit 0;;
esac

#if [ $combin == "1" ];then
#	if [ -f flashtool/system.img ] && [ ! -e Y${main}${BN}${sub}AN00.mbn  ]; then ln -s flashtool/system.img Y${main}${BN}${sub}AN00.mbn; fi 
#else  
#	if [ -f flashtool/custpack.img ] && [ ! -e C${main}${BN}${sub}AN00.mbn ] ; then ln -s flashtool/custpack.img C${main}${BN}${sub}AN00.mbn; #fi  
#fi 
#if [ -f flashtool/secro.img ] && [ ! -e X${main:0:2}0${main:3:1}0${perso}${sub}AN00.mbn  ]; then ln -s flashtool/secro.img X${main:0:2}0${main:3:1}0#${perso}${sub}AN00.mbn; fi
#if [ -f flashtool/logo.bin ] && [ ! -e L${main}0${perso}${sub}AN00.mbn ]; then ln -s flashtool/logo_jrd.bin L${main}0${perso}${sub}AN00.mbn; fi


