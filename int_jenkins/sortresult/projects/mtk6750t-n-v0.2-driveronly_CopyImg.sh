#!/bin/bash

JOB_NAME=$1
version=$2
project=$3

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
   builddir="/local/mtk_patch_import/${JOB_NAME}"
   releasedir="/local/release/${JOB_NAME}/v${version}"
else
   echo -e "$0 build-path version [persono] [band]"
   exit
fi

if [ ! -d ${builddir} ]; then ls ${builddir}; echo "Please input correct build path.";exit; fi

echo -e "builddir:$builddir\nreleasedir:$releasedir\nversion:$version perso:$perso band:$band projectname:$project"

rm -rvf ${releasedir}
mkdir -vp ${releasedir}
mkdir -vp "${releasedir}"

cp ${builddir}/out/target/product/${project}/MT6750*_Android_scatter.txt ${releasedir}
cp ${builddir}/out/target/product/${project}/MT6750*_Android_scatter_emmc.txt ${releasedir} 

cp ${builddir}/out/target/product/${project}/protect_f.imcdgmnuvxg ${releasedir}
cp ${builddir}/out/target/product/${project}/preloader_${project}.bin ${releasedir}
cp ${builddir}/out/target/product/${project}/DSP_BL ${releasedir}
cp ${builddir}/out/target/product/${project}/trustzone.bin ${releasedir}
cp ${builddir}/bootable/bootloader/uboot/uboot_${project}.bin ${releasedir}
cp ${builddir}/out/target/product/${project}/lk.bin ${releasedir}
cp ${builddir}/out/target/product/${project}/boot.img ${releasedir}
cp ${builddir}/out/target/product/${project}/recovery.img ${releasedir}
cp ${builddir}/out/target/product/${project}/system.img ${releasedir}
cp ${builddir}/out/target/product/${project}/cache.img ${releasedir}
cp ${builddir}/out/target/product/${project}/userdata.img ${releasedir}
cp ${builddir}/out/target/product/${project}/logo.bin ${releasedir}
cp ${builddir}/out/target/product/${project}/secro.img ${releasedir}
cp ${builddir}/out/target/product/${project}/previous_build_config.mk ${releasedir}
cp ${builddir}/out/target/product/${project}/proinfo.bin ${releasedir}
cp ${builddir}/out/target/product/${project}/tctpersist.img ${releasedir}
cp ${builddir}/mediatek/build/tools/ptgen/fat.img ${releasedir}
APDBWEEK_NO=`cat ${builddir}/device/jrdchz/${project}/ProjectConfig.mk | awk '{print $3}' | grep ^W[1-9][[:alnum:]]`
cp ${builddir}/out/target/product/${project}/obj/CGEN/APDB_MT6755_S01_alps-mp-n0.mp7_${APDBWEEK_NO} ${releasedir}
cp ${builddir}/modem/mcu/temp_modem/MDDB_InfoCustomAppSrcP* ${releasedir}
cp ${builddir}/out/target/product/${project}/md1rom.img ${releasedir}
cp ${builddir}/out/target/product/${project}/md1arm7.img ${releasedir}
cp ${builddir}/out/target/product/${project}/md3rom.img ${releasedir}
cp ${builddir}/out/target/product/${project}/md1dsp.img ${releasedir}
cp ${builddir}/out/target/product/${project}/target_files_extract.zip ${releasedir}
cp ${builddir}/out/target/product/${project}/_system.map ${releasedir}


