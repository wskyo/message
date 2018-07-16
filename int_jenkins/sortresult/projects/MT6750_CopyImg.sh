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
   Band refer to band mapping table below:\n\tEU:EU\n\tUS: U0\n\tUS1:U1\n\tUS2:U2\n\tAWS:AW\n\tpanasonic:PA"
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
   if [ ${#version} -gt 4 ] || [[ ${version:2:1} =~ [N-Z] ]]; then
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
#mkdir -vp "${releasedir}/mtxgen-config"
if [[ ${version:2:1} =~ [N-Z] ]]; then
	mkdir -vp "${releasedir}/mtxgen"
fi

main=${version:0:4}
if [ ${#version} -gt 4 ]; then
	sub=${version:5:1}
else
	sub=0
fi

echo "sub number"
echo ${sub}

cp ${builddir}/out/target/product/${project}/MT6750*_Android_scatter.txt ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/MT6750*_Android_scatter_emmc.txt ${releasedir}/flashtool 

#cp ${builddir}/mediatek/misc/MT65*_Android_scatter.txt ${releasedir}/flashtool
#cp ${builddir}/mediatek/misc/MT65*_Android_scatter_emmc.txt ${releasedir}/flashtool 

cp ${builddir}/out/target/product/${project}/protect_f.imcdgmnuvxg ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/preloader_${project}.bin ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/DSP_BL ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/trustzone-verified.bin ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/MBR ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/EBR1 ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/EBR2 ${releasedir}/flashtool
cp ${builddir}/bootable/bootloader/uboot/uboot_${project}.bin ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/lk-verified.bin ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/boot-verified.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/recovery-verified.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/system.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/cache.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/userdata.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/logo-verified.bin ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/custpack.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/secro.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/simlock.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/previous_build_config.mk ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/proinfo.bin ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/tctpersist.img ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/EBR3 ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/EBR4 ${releasedir}/flashtool
cp ${builddir}/mediatek/build/tools/ptgen/fat.img ${releasedir}/flashtool
#cp ${builddir}/mediatek/cgen/APDB_MT6572_S01_MAIN2.1_W10.24 ${releasedir}/flashtool
#cp ${builddir}/*_wimdata_ng/wcustores/${project}/Modem/${band}/BPLGUInfo* ${releasedir}/flashtool
APDBWEEK_NO=`cat ${builddir}/device/jrdchz/${project}/ProjectConfig.mk | awk '{print $3}' | grep ^W[1-9][[:alnum:]]`
cp ${builddir}/out/target/product/${project}/obj/CGEN/APDB_MT6755_S01_alps-mp-n0.mp7_${APDBWEEK_NO} ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/obj/CGEN/APDB_MT6580_S01_L1.MP6_W15.20 ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/obj/CUSTGEN/custom/modem/BPLGUInfo* ${releasedir}/flashtool

#cp ${builddir}/mediatek/custom/common/modem/mt6572_demo_hspa_gemini/BPLGUInfo* ${releasedir}/flashtool
cp ${builddir}/modem/mcu/temp_modem/MDDB_InfoCustomAppSrcP* ${releasedir}/flashtool
#cp ${builddir}/vendor/mediatek/proprietary/modem/mt6750_sp_lwctg_mp3_umoly0036_prod/MDDB_InfoCustomAppSrcP* ${releasedir}/flashtool
#cp ${builddir}/vendor/mediatek/proprietary/modem/mt6750_sp_lwctg_mp3_umoly0036_prod/mcddll.dll ${releasedir}/flashtool
#cp ${builddir}/modem/mtk_rel/PIXI4_4_HSPA/DEFAULT/tst/database/mcddll.dll ${releasedir}/flashtool
if [[ ${version:2:1} =~ [N-Z] ]]; then
   cp ${builddir}/out/target/product/${project}/MTXGen/.\\output/* ${releasedir}/mtxgen
   cp ${builddir}/out/target/product/${project}/MTXGen/config/emmc.layout.xml ${releasedir}/mtxgen
fi
#cp ${builddir}/out/target/product/${project}/MTXGen/config/* ${releasedir}/mtxgen-config
cp ${builddir}/out/target/product/${project}/md1rom-verified.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/md1arm7-verified.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/md3rom.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/md1dsp-verified.img ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/target_files_extract.zip ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/_system.map ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/efuse.img ${releasedir}/flashtool


cd ${releasedir}
if [ -d flashtool ]; then
   chmod -R 777 flashtool/*
fi
if [ -d mtxgen ]; then
   #chmod -R 777 mtxgen-config/*
   chmod -R 777 mtxgen/*
fi
if [ -f flashtool/MT6750*_Android_scatter_emmc.txt ]; then ln -s flashtool/MT6750*_Android_scatter_emmc.txt K${main:0:3}EMMCCH00.sca; fi
if [ -f flashtool/MT6750*_Android_scatter.txt ]; then ln -s flashtool/MT6750*_Android_scatter.txt K${main}0${perso}${sub}CH00.sca; fi
if [ -f flashtool/preloader_${project}.bin ]; then ln -s flashtool/preloader_${project}.bin P${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/DSP_BL ]; then ln -s flashtool/DSP_BL D${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/MBR ]; then ln -s flashtool/MBR M${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/EBR1 ]; then ln -s flashtool/EBR1 E${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/lk-verified.bin ]; then ln -s flashtool/lk-verified.bin U${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/boot-verified.img ]; then ln -s flashtool/boot-verified.img B${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/recovery-verified.img ]; then ln -s flashtool/recovery-verified.img R${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/EBR2 ]; then ln -s flashtool/EBR2 G${main}0${perso}${sub}CH00.mbn; fi
#if [ -f flashtool/system.img ]; then ln -s flashtool/system.img Y${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/cache.img ]; then ln -s flashtool/cache.img H${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/userdata.img ]; then ln -s flashtool/userdata.img S${main}0${perso}${sub}CH00.mbn; fi

case $band in
    "EU" )
        BN='EU';;
    "APAC" )
        BN='AP';;
    "EU_CA" )
        BN='EC';;
    "LATAM1" )
        BN='L1';;
    "LATAM1_CA" )
	BN='LA';;
    "LATAM2" )
	BN='L2';;
    "LATAM2_CA" )
        BN='LB';;
    "LATAM3" )
        BN='L3';;
    "LATAM3_CA" )
        BN='LC';;
    "MEA" )
        BN='ME';;
    "US1" )
        BN='U1';;
    "US2" )
        BN='U2';;
    "US3" )
        BN='U3';;
    "2M" )
        BN='2M';;
    "CN" )
        BN='CN';;
    "panasonic" )
        BN='PA';;
    * )
        echo "No such band! (EU|EU_CA|LATAM1|LATAM2|LATAM3|LATAM1_CA|LATAM2_CA|LATAM3_CA|APAC|MEA|US1|US2|US3|panasonic|AP|CN)"
        exit 0;;
esac

if [ ${#version} -gt 4 ] || [[ ${version:2:1} =~ [N-Z] ]] ; then
   if [ -f flashtool/system.img ]; then ln -s flashtool/system.img Y${main}${BN}${sub}CH00.mbn; fi   
   if [ -f flashtool/md1rom-verified.img ]; then  ln -s flashtool/md1rom-verified.img D${main}0${perso}${sub}CH00.mbn; fi  
   if [ -f flashtool/logo-verified.bin ]; then ln -s flashtool/logo-verified.bin L${main}0${perso}${sub}CH00.mbn; fi    
   if [ -f flashtool/_system.img ]; then ln -s flashtool/_system.img 8${main}0${perso}${sub}CH00.mbn; fi  
   if [ -f flashtool/simlock.img ]; then ln -s flashtool/simlock.img X${main}0${perso}${sub}CH00.mbn; fi  

fi
if [ -f flashtool/secro.img ]; then  ln -s flashtool/secro.img W${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/md1arm7-verified.img ]; then  ln -s flashtool/md1arm7-verified.img F${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/md1dsp-verified.img ]; then  ln -s flashtool/md1dsp-verified.img E${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/EBR3 ]; then ln -s flashtool/EBR3 J${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/EBR4 ]; then ln -s flashtool/EBR4 N${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/md3rom.img ]; then  ln -s flashtool/md3rom.img G${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/fat.img ]; then ln -s flashtool/fat.img F${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/tctpersist.img ]; then ln -s flashtool/tctpersist.img I${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/APDB_MT6755* ]; then ln -s flashtool/APDB_MT6755* A${main}0${perso}${sub}CH00.db; fi
#if [ -f flashtool/MCDDLL.dll ]; then ln -s flashtool/MCDDLL.dll MCDDLL.dll; fi
if [ -f flashtool/MDDB_InfoCustomAppSrcP* ]; then ln -s flashtool/MDDB_InfoCustomAppSrcP* O${main}0${perso}${sub}CH00.db; fi
if [ -f flashtool/proinfo.bin ]; then ln -s flashtool/proinfo.bin O${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/trustzone-verified.bin ]; then ln -s flashtool/trustzone-verified.bin T${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/target_files_extract.zip ]; then  ln -s flashtool/target_files_extract.zip 7${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/efuse.img ]; then ln -s flashtool/efuse.img V${main}0${perso}${sub}CH00.mbn; fi

