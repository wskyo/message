#!/bin/bash

JOB_NAME=$1
version=$2
perso=$3
band=$4
project=$5

echo "$5 test for paraments"

if [ -z $1 ] || [ -z $2 ]; then
   echo -e "$0 JOB-NAME|build-path version [persono] [band]
   For example:$0 beetlelite-release B52 2 U0
   Band refer to band mapping table below:\n\tEU:EU\n\tUS_DTV:US\n\tUS: U0\n\tUS1:U1\n\tUS2:U2\n\tAWS:AW\n\tpanasonic:PA"
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
   echo -e "$0 build-path version [persono] [band]"
   exit
fi

if [ ! -d ${builddir} ]; then ls ${builddir}; echo "Please input correct build path.";exit; fi

if [[ ! $2 =~ ^[0-9A-Z][0-9A-Z][0-9A-Z]-[0-9A-Z]|^[0-9A-Z][0-9A-Z][0-9A-Z] ]]; then
   echo "Error: version Number error!"
   echo "please give version like D52 or D5A-4([0-9A-Z][0-9A-Z][0-9A-Z]-[0-9A-Z] or [0-9A-Z][0-9A-Z][0-9A-Z])"
   exit
fi

if [ -z $3 ]; then
   if [ ${#version} -gt 4 ] || [[ ${version:2:1} =~ [U-Z] ]]; then
      perso=0
   else
      perso=${version:3:1}
   fi
   echo "Use default perso number:${perso}"
else
   if [ ${#3} == "1" ]; then
      perso=$3
   else 
      echo "perso=$3"
      echo "Error: please input right perso num!" 
      exit
   fi
fi

echo -e "builddir:$builddir\nreleasedir:$releasedir\nversion:$version perso:$perso band:$band projectname:$project"

rm -rvf ${releasedir}
mkdir -vp ${releasedir}
mkdir -vp "${releasedir}/flashtool"

main=${version:0:4}
if [ ${#version} -gt 4 ]; then
	sub=${version:5:1}
else
	sub=0
fi

echo "sub number"
echo ${sub}
echo ${project}

cp ${builddir}/out/target/product/${project}/MT65*_Android_scatter.txt ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/MT65*_Android_scatter_emmc.txt ${releasedir}/flashtool 

cp ${builddir}/mediatek/misc/MT65*_Android_scatter.txt ${releasedir}/flashtool
#cp ${builddir}/mediatek/misc/MT65*_Android_scatter_emmc.txt ${releasedir}/flashtool 

cp ${builddir}/out/target/product/${project}/protect_f.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/preloader_${project}.bin ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/DSP_BL ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/mobile_info.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/MBR ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/EBR1 ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/EBR2 ${releasedir}/flashtool
#cp ${builddir}/bootable/bootloader/uboot/uboot_${project}.bin ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/lk.bin ${releasedir}/flashtool
if [ -f ${builddir}/out/target/product/${project}/lk.bin ]; then
   cp ${builddir}/out/target/product/${project}/lk.bin ${releasedir}/flashtool;
else
   cp ${builddir}/out/target/product/${project}/uboot_*.bin ${releasedir}/flashtool;
fi

cp ${builddir}/out/target/product/${project}/boot.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/recovery.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/system.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/cache.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/userdata.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/logo.bin ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/custpack.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/secro.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/previous_build_config.mk ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/EBR3 ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/EBR4 ${releasedir}/flashtool
cp ${builddir}/mediatek/misc/EBR3 ${releasedir}/flashtool
cp ${builddir}/mediatek/misc/EBR4 ${releasedir}/flashtool

cp ${builddir}/mediatek/build/tools/ptgen/fat.img ${releasedir}/flashtool
#cp ${builddir}/mediatek/cgen/APDB_MT6572_S01_MAIN2.1_W10.24 ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/obj/CODEGEN/cgen/APDB_MT657*_S01_KK_  ${releasedir}/flashtool ${releasedir}/flashtool
cp ${builddir}/mediatek/cgen/APDB2* ${releasedir}/flashtool
#cp ${builddir}/*_wimdata_ng/wcustores/${project}/Modem/${band}/BPLGUInfo* ${releasedir}/flashtool
#cp ${builddir}/modem/out_modem/BPLGUInfo* ${releasedir}/flashtool
cp ${builddir}/*_wimdata_ng/wcustores/${project}/Modem/${band}/BPLGUInfo* ${releasedir}/flashtool
cp ${builddir}/*_wimdata_ng/wcustores/${project}/Modem/${band}/mcddll.dll ${releasedir}/flashtool

#cp ${builddir}/mediatek/custom/common/modem/mt6572_demo_hspa_gemini/BPLGUInfo* ${releasedir}/flashtool
#cp ${builddir}/mediatek/custom/common/modem/mt6572_demo_hspa_gemini/MCDDLL.dll ${releasedir}/flashtool
#cp ${builddir}/mediatek/custom/common/modem/mt6572_demo_hspa_gemini/mcddll.dll ${releasedir}/flashtool
#cp ${builddir}/*_wimdata_ng/wcustores/${project}/Modem/${band}/MCDDLL.dll ${releasedir}/flashtool
#cp ${builddir}/*_wimdata_ng/wcustores/${project}/Modem/${band}/mcddll.dll ${releasedir}/flashtool
#cp ${builddir}/*_wimdata_ng/wcustores/${project}/Modem/${band}/mcddll.dll ${releasedir}/flashtool./modem/service/tst/database/MCDDLL.dll


cd ${releasedir}
if [ -d flashtool ]; then
   chmod -R 777 flashtool/*
fi
if [ -f flashtool/MT657*_Android_scatter.txt ]; then ln -s flashtool/MT657*_Android_scatter.txt K${main:1:3}EMMC.sca; fi
if [ -f flashtool/preloader_*.bin ]; then ln -s flashtool/preloader_*.bin P${main}0${perso}${sub}AN00.mbn; fi
if [ -f flashtool/DSP_BL ]; then ln -s flashtool/DSP_BL D${main}0${perso}${sub}AN00.mbn; fi
if [ -f flashtool/MBR ]; then ln -s flashtool/MBR M${main}0${perso}${sub}AN00.mbn; fi
if [ -f flashtool/EBR1 ]; then ln -s flashtool/EBR1 E${main}0${perso}${sub}AN00.mbn; fi
if [ -f flashtool/uboot_*.bin ]; then ln -s flashtool/uboot_*.bin U${main}0${perso}${sub}AN00.mbn; else ln -s flashtool/lk.bin U${main}0${perso}${sub}AN00.mbn; fi
if [ -f flashtool/boot.img ]; then ln -s flashtool/boot.img B${main}0${perso}${sub}AN00.mbn; fi
if [ -f flashtool/recovery.img ]; then ln -s flashtool/recovery.img R${main}0${perso}${sub}AN00.mbn; fi
if [ -f flashtool/EBR2 ]; then ln -s flashtool/EBR2 G${main}0${perso}${sub}AN00.mbn; fi
if [ -f flashtool/system.img ]; then ln -s flashtool/system.img Y${main}0${perso}${sub}AN00.mbn; fi
if [ -f flashtool/cache.img ]; then ln -s flashtool/cache.img H${main}0${perso}${sub}AN00.mbn; fi
if [ -f flashtool/userdata.img ]; then ln -s flashtool/userdata.img S${main}0${perso}${sub}AN00.mbn; fi
if [ -f flashtool/secro.img ]; then ln -s flashtool/secro.img V${main:0:2}0${main:3:1}0${perso}${sub}AN00.mbn; fi

case $band in
    "EU" )
        BN='EU';;
    "US" )
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
    "2M" )
        BN='2M';;
    "panasonic" )
        BN='PA';;
    "US_DTV" )
        BN='US';;
    "EU_DTV" )
        BN='EU';;
    "US_ATV" )
        BN='US';;
    "USF_ATV" )
        BN='US';;
    * )
        echo "No such band! (EU|US|US1|US2|2M|AWS|LATAM2G|LATAM3G|panasonic|US_DTV|US_ATV|USF_ATV|EU_DTV)"
        exit 0;;
esac

if [ ${#version} -gt 4 ] || [[ ${version:2:1} =~ [U-Z] ]] || [[ ${version:2:1} =~ [6] ]]; then
#   if [ -f flashtool/custpack.img ]; then ln -s flashtool/custpack.img C${main}${BN}${sub}AN00.mbn; fi   
#   if [ -f flashtool/secro.img ]; then  ln -s flashtool/secro.img X${main}0${perso}${sub}AN00.mbn; fi
#   if [ -f flashtool/logo*.bin ]; then ln -s flashtool/logo*.bin L${main}0${perso}${sub}AN00.mbn; fi  
   if [ -f flashtool/custpack.img ]; then ln -s flashtool/custpack.img C${main}${BN}${sub}AN00.mbn; fi
   if [ -f flashtool/protect_f.img ]; then ln -s flashtool/protect_f.img X${main:0:2}0${main:3:1}0${perso}${sub}AN00.mbn; fi
   if [ -f flashtool/logo.bin ]; then ln -s flashtool/logo.bin L${main}0${perso}${sub}AN00.mbn; fi
   if [ -f flashtool/fat.img ]; then ln -s flashtool/fat.img F${main}0${perso}${sub}AN00.mbn; fi
 
fi
#if [ -f flashtool/EBR3 ]; then ln -s flashtool/EBR3 J${main}0${perso}${sub}AN00.mbn; fi
#if [ -f flashtool/EBR4 ]; then ln -s flashtool/EBR4 N${main}0${perso}${sub}AN00.mbn; fi
#if [ -f flashtool/fat.img ]; then ln -s flashtool/fat.img F${main}0${perso}${sub}AN00.mbn; fi
#if [ -f flashtool/mobile_info.img ]; then ln -s flashtool/mobile_info.img I${main}0${perso}${sub}AN00.mbn; fi
#if [ -f flashtool/APDB_MT6572* ]; then ln -s flashtool/APDB_MT6572* A${main}0${perso}${sub}AN00.db; fi
#if [ -f flashtool/MCDDLL.dll ]; then ln -s flashtool/MCDDLL.dll MCDDLL.dll; fi
#if [ -f flashtool/BPLGUInfoCustomAppSrcP* ]; then ln -s flashtool/BPLGUInfoCustomAppSrcP* O${main}0${perso}${sub}AN00.db; fi

if [ -f flashtool/EBR3 ]; then ln -s flashtool/EBR3 J${main}0${perso}${sub}AN00.mbn; fi
if [ -f flashtool/EBR4 ]; then ln -s flashtool/EBR4 N${main}0${perso}${sub}AN00.mbn; fi
if [ -f flashtool/mobile_info.img ]; then ln -s flashtool/mobile_info.img I${main}0${perso}${sub}AN00.mbn; fi
if [ -f flashtool/BPLGUInfo*EU* ]; then 
  ln -s flashtool/BPLGUInfo* O${main}EU${sub}AN00.db;
  if [ -f flashtool/APDB* ]; then ln -s flashtool/APDB* A${main}EU${sub}AN00.db; fi
elif [ -f flashtool/BPLGUInfo*US* ]; then
  ln -s flashtool/BPLGUInfo* O${main}US${sub}AN00.db;
  if [ -f flashtool/APDB* ]; then ln -s flashtool/APDB* A${main}US${sub}AN00.db; fi
elif [ -f flashtool/BPLGUInfo*AWS* ]; then
  ln -s flashtool/BPLGUInfo* O${main}AW${sub}AN00.db;
  if [ -f flashtool/APDB* ]; then ln -s flashtool/APDB* A${main}AW${sub}AN00.db; fi
else
  ln -s flashtool/BPLGUInfo* O${main}0${perso}${sub}AN00.db;
  if [ -f flashtool/APDB* ]; then ln -s flashtool/APDB* A${main}0${perso}${sub}AN00.db; fi
fi



