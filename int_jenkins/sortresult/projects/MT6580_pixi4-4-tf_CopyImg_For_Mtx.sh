#!/bin/bash

JOB_NAME=$1
version=$2
mtkProject=$3


if [ -z $1 ] || [ -z $2 ]; then
   echo -e "$0 JOB-NAME|build-path version
   For example:$0 beetlelite-release B52"
   exit
fi


builddir="/local/build/${JOB_NAME}/v${version}/out/target/product/${mtkProject}/signed_bin"
releasedir="/local/build/${JOB_NAME}/v${version}/out/target/product/${mtkProject}/mtximg"

if [ ! -d ${builddir} ]; then ls ${builddir}; echo "Please input correct build path.";exit; fi

echo -e "builddir:$builddir\nreleasedir:$releasedir\nversion:$version"

rm -rvf ${releasedir}
mkdir -vp ${releasedir}

#cp ${builddir}/MT65*_Android_scatter.txt ${releasedir}/
cp ${builddir}/mobile_info-sign.img ${releasedir}/
cp ${builddir}/lk-sign.bin ${releasedir}/
cp ${builddir}/proinfo-sign.bin ${releasedir}/
cp ${builddir}/boot-sign.img ${releasedir}/
cp ${builddir}/recovery-sign.img ${releasedir}/
cp ${builddir}/system-sign.img ${releasedir}/
cp ${builddir}/cache-sign.img ${releasedir}/
cp ${builddir}/userdata-sign.img ${releasedir}/
cp ${builddir}/logo-sign.bin ${releasedir}/
cp ${builddir}/custpack-sign.img ${releasedir}/
cp ${builddir}/secro-sign.img ${releasedir}/
cp ${builddir}/simlock-sign.img ${releasedir}/
cp ${builddir}/trustzone-sign.bin ${releasedir}/
cp ${builddir}/mobile_info-sign.img ${releasedir}/
cp /local/build/${JOB_NAME}/v${version}/out/target/product/${mtkProject}/MT6580_Android_scatter.txt ${releasedir}
cp /local/build/${JOB_NAME}/v${version}/out/target/product/${mtkProject}/preloader_pixi4_4_tf.bin ${releasedir}/
