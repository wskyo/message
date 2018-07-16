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

cp ${builddir}/out/target/product/${project}/MT65*_Android_scatter.txt ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/MT65*_Android_scatter_emmc.txt ${releasedir}/flashtool 

#cp ${builddir}/mediatek/misc/MT65*_Android_scatter.txt ${releasedir}/flashtool
#cp ${builddir}/mediatek/misc/MT65*_Android_scatter_emmc.txt ${releasedir}/flashtool 

cp ${builddir}/out/target/product/${project}/protect_f.imcdgmnuvxg ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/preloader_${project}.bin ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/DSP_BL ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/mobile_info.img ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/MBR ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/EBR1 ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/EBR2 ${releasedir}/flashtool
cp ${builddir}/bootable/bootloader/uboot/uboot_${project}.bin ${releasedir}/flashtool
cp ${builddir}/out/target/product/${project}/lk.bin ${releasedir}/flashtool
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
cp ${builddir}/mediatek/build/tools/ptgen/fat.img ${releasedir}/flashtool
#cp ${builddir}/mediatek/cgen/APDB_MT6572_S01_MAIN2.1_W10.24 ${releasedir}/flashtool
#cp ${builddir}/*_wimdata_ng/wcustores/${project}/Modem/${band}/BPLGUInfo* ${releasedir}/flashtool
APDBWEEK_NO=`cat ${builddir}/device/jrdchz/${project}/ProjectConfig.mk | awk '{print $3}' | grep W16`
cp ${builddir}/out/target/product/${project}/obj/CGEN/APDB_MT6580_S01_L1.MP6_${APDBWEEK_NO} ${releasedir}/flashtool
#cp ${builddir}/out/target/product/${project}/obj/CUSTGEN/custom/modem/BPLGUInfo* ${releasedir}/flashtool

#cp ${builddir}/mediatek/custom/common/modem/mt6572_demo_hspa_gemini/BPLGUInfo* ${releasedir}/flashtool
cp ${builddir}/modem/out_modem/BPLGUInfo* ${releasedir}/flashtool
#cp ${builddir}/mediatek/custom/common/modem/jrdhz72_we_72_s1_kk/MCDDLL.dll ${releasedir}/flashtool
#cp ${builddir}/mediatek/custom/common/modem/jrdhz72_we_72_s1_kk/mcddll.dll ${releasedir}/flashtool
cp ${builddir}/modem/mtk_rel/PIXI3_55_HSPA/DEFAULT/tst/database/MCDDLL.dll ${releasedir}/flashtool
cp ${builddir}/modem/mtk_rel/PIXI3_55_HSPA/DEFAULT/tst/database/mcddll.dll ${releasedir}/flashtool


cd ${releasedir}
if [ -d flashtool ]; then
   chmod -R 777 flashtool/*
fi
if [ -f flashtool/MT65*_Android_scatter_emmc.txt ]; then ln -s flashtool/MT65*_Android_scatter_emmc.txt K${main:0:3}EMMCBV00.sca; fi
if [ -f flashtool/MT65*_Android_scatter.txt ]; then ln -s flashtool/MT65*_Android_scatter.txt K${main}0${perso}${sub}BV00.sca; fi
if [ -f flashtool/preloader_${project}.bin ]; then ln -s flashtool/preloader_${project}.bin P${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/DSP_BL ]; then ln -s flashtool/DSP_BL D${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/MBR ]; then ln -s flashtool/MBR M${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/EBR1 ]; then ln -s flashtool/EBR1 E${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/lk.bin ]; then ln -s flashtool/lk.bin U${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/boot.img ]; then ln -s flashtool/boot.img B${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/recovery.img ]; then ln -s flashtool/recovery.img R${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/EBR2 ]; then ln -s flashtool/EBR2 G${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/system.img ]; then ln -s flashtool/system.img Y${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/cache.img ]; then ln -s flashtool/cache.img H${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/userdata.img ]; then ln -s flashtool/userdata.img S${main}0${perso}${sub}BV00.mbn; fi

case $band in
    "EU" )
        BN='EU';;
    "US" )
        BN='U0';;
    "US0" )
        BN='U0';;
    "US4" )
	BN='U4';;
    "US5" )
	BN='U5';;
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
    "US3" )
        BN='U3';;
    "2M" )
        BN='2M';;
    "panasonic" )
        BN='PA';;
    * )
        echo "No such band! (EU|US|US0|US1|US2|US3|2M|AWS|LATAM2G|LATAM3G|panasonic)"
        exit 0;;
esac

if [ ${#version} -gt 4 ] || [[ ${version:2:1} =~ [U-Z] ]] || [[ ${version:2:1} =~ [6] ]]; then
   if [ -f flashtool/custpack.img ]; then ln -s flashtool/custpack.img C${main}${BN}${sub}BV00.mbn; fi   
   if [ -f flashtool/secro.img ]; then  ln -s flashtool/secro.img X${main}0${perso}${sub}BV00.mbn; fi
   if [ -f flashtool/logo*.bin ]; then ln -s flashtool/logo*.bin L${main}0${perso}${sub}BV00.mbn; fi   
fi
if [ -f flashtool/EBR3 ]; then ln -s flashtool/EBR3 J${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/EBR4 ]; then ln -s flashtool/EBR4 N${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/fat.img ]; then ln -s flashtool/fat.img F${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/mobile_info.img ]; then ln -s flashtool/mobile_info.img I${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/APDB_MT6580* ]; then ln -s flashtool/APDB_MT6580* A${main}0${perso}${sub}BV00.db; fi
#if [ -f flashtool/MCDDLL.dll ]; then ln -s flashtool/MCDDLL.dll MCDDLL.dll; fi
if [ -f flashtool/BPLGUInfoCustomAppSrcP* ]; then ln -s flashtool/BPLGUInfo* O${main}0${perso}${sub}BV00.db; fi
