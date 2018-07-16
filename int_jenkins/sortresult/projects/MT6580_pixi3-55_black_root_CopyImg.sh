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


releasedir="/local/release/${JOB_NAME}/v${version}"
builddir="/local/black/${JOB_NAME}/v${version}"


if [ ! -d ${builddir} ]; then ls ${builddir}; echo "Please input correct build path.";exit; fi

echo -e "builddir:$builddir\nreleasedir:$releasedir\nversion:$version projectname:$project"

if [ -e ${builddir}/out/target/product/${project}/boot.img ]
then 
	cp ${builddir}/out/target/product/${project}/boot.img ${releasedir}/flashtool/rootboot.img
else 
	echo "there is no boot.img when build"
 	exit 0
fi
if [ -e ${builddir}/out/target/product/${project}/lk.bin ]
then 
	cp ${builddir}/out/target/product/${project}/lk.bin ${releasedir}/flashtool/rootlk.bin
else 
	echo "there is no lk.bin when build"
 	exit 0
fi
echo "copy rootlk.bin successfully"
