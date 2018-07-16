#!/bin/bash

JOB_NAME=$1
version=$2
#perso=$3
#band=$4
project=$3

echo "$5 test for paraments"

if [ -z $1 ] || [ -z $2 ]; then
   echo -e "$0 JOB-NAME|build-path version
   For example:$0 beetlelite-release B52 2
   "
   exit
fi

if [ -d $1 ]; then
   tmpPath=`cd $1 && pwd`
   if [[ $tmpPath =~ .*\/$ ]]; then tmpPath="${tmpPath:0:${#1}-1}"; fi
else
   tmpPath=$1
fi
if [[ $tmpPath =~ ^\/.*\/.* ]]; then
   builddir=${tmpPath}
   releasedir="${tmpPath}/v${version}"
elif [[ ! $tmpPath =~ ^\/.* ]]; then
   builddir="/local/build/${JOB_NAME}/v${version}"
   releasedir="/local/release/${JOB_NAME}/v${version}"
else
   echo -e "$0 build-path version"
   exit
fi

if [ ! -d ${builddir} ]; then ls ${builddir}; echo "Please input correct build path.";exit; fi

if [[ ! $2 =~ ^[0-9A-Z][0-9A-Z][0-9A-Z]-[0-9A-Z]|^[0-9A-Z][0-9A-Z][0-9A-Z] ]]; then
   echo "Error: version Number error!"
   echo "please give version like D52 or D5A-4([0-9A-Z][0-9A-Z][0-9A-Z]-[0-9A-Z] or [0-9A-Z][0-9A-Z][0-9A-Z])"
   exit
fi


echo -e "builddir:$builddir\nreleasedir:$releasedir\nversion:$version projectname:$project"

if [ -e ${builddir}/out/target/product/${project}/boot-verified.img ]; then 
	cp ${builddir}/out/target/product/${project}/boot-verified.img ${releasedir}/flashtool/rootboot-verified.img
elif [ -e ${builddir}/out/target/product/${project}/boot.img ]; then 
        cp ${builddir}/out/target/product/${project}/boot.img ${releasedir}/flashtool/rootboot.img
else 
	echo "there is no boot.img when build"
 	exit 0
fi
if [ -e ${builddir}/out/target/product/${project}/lk-verified.bin ];then 
	cp ${builddir}/out/target/product/${project}/lk-verified.bin ${releasedir}/flashtool/rootlk-verified.bin
elif [ -e ${builddir}/out/target/product/${project}/lk.bin ];then
	cp ${builddir}/out/target/product/${project}/lk.bin ${releasedir}/flashtool/rootlk.bin

else 
	echo "there is no lk.bin when build"
 	exit 0
fi
echo "copy rootlk.bin successfully"
