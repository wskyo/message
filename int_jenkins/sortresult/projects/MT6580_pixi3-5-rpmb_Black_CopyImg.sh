#!/bin/bash

JOB_NAME=$1
baseversion=$2
blacksuffix=$3
band=$4
project=$5


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

rm -rvf ${relaseblackdir}
mkdir -vp ${relaseblackdir}
mkdir -vp "${relaseblackdir}/flashtool"
mkdir -vp "${relaseblackdir}/mtxgen"


cp ${buildblackdir}/out/target/product/${project}/MT65*_Android_scatter.txt ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/MT65*_Android_scatter_emmc.txt ${relaseblackdir}/flashtool 

#cp ${buildblackdir}/mediatek/misc/MT65*_Android_scatter.txt ${relaseblackdir}/flashtool
#cp ${buildblackdir}/mediatek/misc/MT65*_Android_scatter_emmc.txt ${relaseblackdir}/flashtool 

cp ${buildblackdir}/out/target/product/${project}/preloader_${project}.bin ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/DSP_BL ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/signed_bin/mobile_info-sign.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/MBR ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/EBR1 ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/EBR2 ${relaseblackdir}/flashtool
cp ${buildblackdir}/bootable/bootloader/uboot/uboot_${project}.bin ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/signed_bin/lk-sign.bin ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/signed_bin/boot-sign.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/signed_bin/recovery-sign.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/signed_bin/system-sign.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/signed_bin/cache-sign.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/signed_bin/userdata-sign.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/signed_bin/logo-sign.bin ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/signed_bin/custpack-sign.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/signed_bin/secro-sign.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/signed_bin/simlock-sign.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/signed_bin/trustzone-sign.bin ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/previous_build_config.mk ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/EBR3 ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/EBR4 ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/fat.img ${relaseblackdir}/flashtool
#cp ${buildblackdir}/mediatek/cgen/APDB_MT6572_S01_MAIN2.1_W10.24 ${relaseblackdir}/flashtool
#cp ${builddir}/*_wimdata_ng/wcustores/Modem/${band}/BPLGUInfo* ${relaseblackdir}/flashtool
APDBWEEK_NO=`cat ${buildblackdir}/device/jrdchz/${project}/ProjectConfig.mk | awk '{print $3}' | grep ^W[1-9][[:alnum:]]`
cp ${buildblackdir}/out/target/product/${project}/obj/CGEN/APDB_MT6580_S01_L1.MP6_${APDBWEEK_NO} ${relaseblackdir}/flashtool
#cp ${buildblackdir}/out/target/product/${project}/obj/CGEN/CGEN/APDB_MT6580_S01_L1.MP6_W15.20 ${relaseblackdir}/flashtool
#cp ${buildblackdir}/out/target/product/${project}/obj/CUSTGEN/custom/modem/BPLGUInfo* ${relaseblackdir}/flashtool

cp ${buildblackdir}/modem/out_modem/BPLGUInfo* ${relaseblackdir}/flashtool
#cp ${buildblackdir}/mediatek/custom/common/modem/jrdhz72_we_72_s1_kk/MCDDLL.dll ${relaseblackdir}/flashtool
#cp ${buildblackdir}/mediatek/custom/common/modem/jrdhz72_we_72_s1_kk/mcddll.dll ${relaseblackdir}/flashtool
cp ${buildblackdir}/modem/mtk_rel/PIXI3_5_HSPA/DEFAULT/tst/database/MCDDLL.dll ${relaseblackdir}/flashtool
cp ${buildblackdir}/modem/mtk_rel/PIXI3_5_HSPA/DEFAULT/tst/database/mcddll.dll ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/MTXGen/.\\output/* ${relaseblackdir}/mtxgen
cp ${buildblackdir}/out/target/product/${project}/MTXGen/config/emmc.layout.xml ${relaseblackdir}/mtxgen



cd ${relaseblackdir}
if [ -d flashtool ]; then
   chmod -R 777 flashtool/*
fi
if [ -d mtxgen ]; then
   chmod -R 777 mtxgen/*
fi
if [ -f flashtool/MT65*_Android_scatter_emmc.txt ]; then ln -s flashtool/MT65*_Android_scatter_emmc.txt K${main:0:3}EMMCBV00.sca; fi
if [ -f flashtool/MT65*_Android_scatter.txt ]; then ln -s flashtool/MT65*_Android_scatter.txt K${main}0${perso}${sub}BV00.sca; fi
if [ -f flashtool/preloader_${project}.bin ]; then ln -s flashtool/preloader_${project}.bin P${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/DSP_BL ]; then ln -s flashtool/DSP_BL D${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/MBR ]; then ln -s flashtool/MBR M${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/EBR1 ]; then ln -s flashtool/EBR1 E${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/lk-sign.bin ]; then ln -s flashtool/lk-sign.bin U${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/boot-sign.img ]; then ln -s flashtool/boot-sign.img B${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/recovery-sign.img ]; then ln -s flashtool/recovery-sign.img R${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/EBR2 ]; then ln -s flashtool/EBR2 G${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/system-sign.img ]; then ln -s flashtool/system-sign.img Y${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/cache-sign.img ]; then ln -s flashtool/cache-sign.img H${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/userdata-sign.img ]; then ln -s flashtool/userdata-sign.img S${main}0${perso}${sub}BV00.mbn; fi

if [ ${#version} -gt 4 ] || [[ ${version:2:1} =~ [T-Z] ]]; then
   if [ -f flashtool/custpack-sign.img ]; then ln -s flashtool/custpack-sign.img C${main}${BN}${sub}BV00.mbn; fi  
   if [ -f flashtool/logo*.bin ]; then ln -s flashtool/logo*.bin L${main}0${perso}${sub}BV00.mbn; fi   
   if [ -f flashtool/simlock-sign.img ]; then  ln -s flashtool/simlock-sign.img X${main}0${perso}${sub}BV00.mbn; fi
fi
if [[ ${version:2:1} =~ [6] ]]; then
   if [ -f flashtool/secro-sign.img ]; then  ln -s flashtool/secro-sign.img W${main}0${perso}${sub}BV00.mbn; fi
fi 

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

#if [ -f flashtool/custpack.img ]; then ln -s flashtool/custpack.img C${main}${BN}${sub}AN00.mbn; fi   
#if [ -f flashtool/secro.img ]; then ln -s flashtool/secro.img X${main:0:2}0${main:3:1}0${perso}${sub}AN00.mbn; fi
#if [ -f flashtool/logo_jrd.bin ]; then ln -s flashtool/logo_jrd.bin L${main}0${perso}${sub}AN00.mbn; fi

if [ -f flashtool/EBR3 ]; then ln -s flashtool/EBR3 J${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/EBR4 ]; then ln -s flashtool/EBR4 N${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/fat.img ]; then ln -s flashtool/fat.img F${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/mobile_info-sign.img ]; then ln -s flashtool/mobile_info-sign.img I${main}0${perso}${sub}BV00.mbn; fi
if [ -f flashtool/APDB_MT6580* ]; then ln -s flashtool/APDB_MT6580* A${main}0${perso}${sub}BV00.db; fi
if [ -f flashtool/BPLGUInfoCustomAppSrcP* ]; then ln -s flashtool/BPLGUInfoCustomAppSrcP* O${main}0${perso}${sub}BV00.db; fi
if [ -f flashtool/trustzone-sign.bin ]; then ln -s flashtool/trustzone-sign.bin T${main}0${perso}${sub}BV00.mbn; fi

if [ -f flashtool/secro-sign.img ]; then  ln -s flashtool/secro-sign.img W${main}0${perso}${sub}BV00.mbn; fi

