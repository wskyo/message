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
   Band refer to band mapping table below:\n\tEU:EU\n\tUS:US"
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
#mkdir -vp "${releasedir}/mtxgen"

main=${version:0:4}
if [ ${#version} -gt 4 ]; then
	sub=${version:5:1}
else
	sub=0
fi

echo "sub number"
echo ${sub}

#Add for copying A file by yufei.qin 20150520
APDBWEEK_NO=`cat ${builddir}/device/jrdchz/jhz6735m_35u_l/ProjectConfig.mk | awk '{print $3}' | grep W15`
echo "APDBWEEK_NO name is ${APDBWEEK_NO}."
#Add end for copying A file by yufei.qin 20150520

cp ${builddir}/out/target/product/${project}/MT67*_Android_scatter.txt ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/preloader_${project}.bin ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/mobile_info.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/lk.bin ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/boot.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/recovery.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/system.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/cache.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/userdata.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/logo.bin ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/custpack.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/secro.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/trustzone.bin ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/obj/CGEN/APDB_MT6735_S01_L1.MP3_${APDBWEEK_NO} ${releasedir}/flashtool
#cp ${builddir}/vendor/mediatek/proprietary/custom/${project}/modem/jrdhz6735m_35u_l_lwg_dsds/BPLGUInfo* ${releasedir}/flashtool
cp ${builddir}/mtk6735_wimdata_ng/wcustores/pixi3_45/Modem/${band}/BPLGUInfo* ${releasedir}/flashtool
cp ${builddir}/mtk6735_wimdata_ng/wcustores/pixi3_45/Modem/${band}/mcddll.dll ${releasedir}/flashtool
#cp ${builddir}/mtk6735_wimdata_ng/wcustores/pixi3_45/Modem/${band}/MCDDLL.dll ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/MTXGen/.\\output/* ${releasedir}/mtxgen
#cp ${builddir}/out/target/product/${project}/MTXGen/config/emmc.layout.xml ${releasedir}/mtxgen
cp ${builddir}/out/target/product/${project}/MTXGen/config/* ${releasedir}/mtxgen-config


cd ${releasedir}
if [ -d flashtool ]; then
   chmod -R 777 flashtool/*
fi
if [ -d mtxgen ]; then
   #chmod -R 777 mtxgen/*
   chmod -R 777 mtxgen-config/*
fi
if [ -f flashtool/MT65*_Android_scatter_emmc.txt ]; then ln -s flashtool/MT65*_Android_scatter_emmc.txt K${main:0:3}EMMCBP00.sca; fi
if [ -f flashtool/MT67*_Android_scatter.txt ]; then ln -s flashtool/MT67*_Android_scatter.txt K${main:0:3}EMMCBP00.sca; fi
if [ -f flashtool/preloader_${project}.bin ]; then ln -s flashtool/preloader_${project}.bin P${main}0${perso}${sub}BP00.mbn; fi
if [ -f flashtool/lk.bin ]; then ln -s flashtool/lk.bin U${main}0${perso}${sub}BP00.mbn; fi
if [ -f flashtool/boot.img ]; then ln -s flashtool/boot.img B${main}0${perso}${sub}BP00.mbn; fi
if [ -f flashtool/recovery.img ]; then ln -s flashtool/recovery.img R${main}0${perso}${sub}BP00.mbn; fi
if [ -f flashtool/system.img ]; then ln -s flashtool/system.img Y${main}0${perso}${sub}BP00.mbn; fi
if [ -f flashtool/cache.img ]; then ln -s flashtool/cache.img H${main}0${perso}${sub}BP00.mbn; fi
if [ -f flashtool/userdata.img ]; then ln -s flashtool/userdata.img S${main}0${perso}${sub}BP00.mbn; fi
if [ -f flashtool/trustzone.bin ]; then ln -s flashtool/trustzone.bin T${main}0${perso}${sub}BP00.mbn; fi

case $band in
    "EU" )
        BN='EU';;
    "US" )
        BN='US';;
    "US_NA" )
        BN='US';;
    "US_DC" )
        BN='US';;
#    "US3" )
#        BN='U3';;
    * )
        echo "No such band! (EU|US|US_NA|US_DC)"
        exit 0;;
esac

if [ ${#version} -gt 4 ] || [[ ${version:2:1} =~ [T|U-Z] ]]; then 
   if [ -f flashtool/secro.img ]; then ln -s flashtool/secro.img X${main:0:2}0${main:3:1}0${perso}${sub}BP00.mbn; fi
   if [ -f flashtool/logo.bin ]; then ln -s flashtool/logo.bin L${main}0${perso}${sub}BP00.mbn; fi
   if [ -f flashtool/custpack.img ]; then ln -s flashtool/custpack.img C${main}${BN}${sub}BP00.mbn; fi
fi

if [ -f flashtool/mobile_info.img ]; then ln -s flashtool/mobile_info.img I${main}0${perso}${sub}BP00.mbn; fi
if [ -f flashtool/APDB_MT6735* ]; then ln -s flashtool/APDB_MT6735* A${main}0${perso}${sub}BP00.db; fi
if [ -f flashtool/mcddll.dll ]; then ln -s flashtool/mcddll.dll mcddll.dll; fi
if [ -f flashtool/BPLGUInfo* ]; then ln -s flashtool/BPLGUInfo* O${main}0${perso}${sub}BP00.db; fi
