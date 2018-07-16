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

cp ${buildblackdir}/out/target/product/${project}/MT67*_Android_scatter.txt ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/MT6750*_Android_scatter_emmc.txt ${relaseblackdir}/flashtool 

cp ${buildblackdir}/out/target/product/${project}/protect_f.imcdgmnuvxg ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/preloader_${project}.bin ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/DSP_BL ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/trustzone-verified.bin ${relaseblackdir}/flashtool
#cp ${buildblackdir}/out/target/product/${project}/MBR ${relaseblackdir}/flashtool
#cp ${buildblackdir}/out/target/product/${project}/EBR1 ${relaseblackdir}/flashtool
#cp ${buildblackdir}/out/target/product/${project}/EBR2 ${relaseblackdir}/flashtool
cp ${buildblackdir}/bootable/bootloader/uboot/uboot_${project}.bin ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/lk-verified.bin ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/boot-verified.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/recovery-verified.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/system.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/cache.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/userdata.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/logo-verified.bin ${relaseblackdir}/flashtool
#cp ${buildblackdir}/out/target/product/${project}/custpack.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/secro.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/simlock.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/previous_build_config.mk ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/proinfo.bin ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/tctpersist.img ${relaseblackdir}/flashtool
#cp ${buildblackdir}/out/target/product/${project}/EBR3 ${relaseblackdir}/flashtool
#cp ${buildblackdir}/out/target/product/${project}/EBR4 ${relaseblackdir}/flashtool
cp ${buildblackdir}/mediatek/build/tools/ptgen/fat.img ${relaseblackdir}/flashtool
#cp ${buildblackdir}/mediatek/cgen/APDB_MT6572_S01_MAIN2.1_W10.24 ${relaseblackdir}/flashtool
#cp ${buildblackdir}/*_wimdata_ng/wcustores/${project}/Modem/${band}/BPLGUInfo* ${relaseblackdir}/flashtool
APDBWEEK_NO=`cat ${buildblackdir}/device/jrdchz/${project}/ProjectConfig.mk | awk '{print $3}' | grep ^W[1-9][[:alnum:]]`
cp ${buildblackdir}/out/target/product/${project}/obj/CGEN/APDB_MT6755_S01_alps-mp-n0.mp7_${APDBWEEK_NO} ${relaseblackdir}/flashtool
#cp ${buildblackdir}/out/target/product/${project}/obj/CGEN/APDB_MT6580_S01_L1.MP6_W15.20 ${relaseblackdir}/flashtool
#cp ${buildblackdir}/out/target/product/${project}/obj/CUSTGEN/custom/modem/BPLGUInfo* ${relaseblackdir}/flashtool

#cp ${buildblackdir}/mediatek/custom/common/modem/mt6572_demo_hspa_gemini/BPLGUInfo* ${relaseblackdir}/flashtool
cp ${buildblackdir}/modem/mcu/temp_modem/MDDB_InfoCustomAppSrcP* ${relaseblackdir}/flashtool
#cp ${buildblackdir}/vendor/mediatek/proprietary/modem/mt6750_sp_lwctg_mp3_umoly0036_prod/MDDB_InfoCustomAppSrcP* ${relaseblackdir}/flashtool
#cp ${buildblackdir}/vendor/mediatek/proprietary/modem/mt6750_sp_lwctg_mp3_umoly0036_prod/mcddll.dll ${relaseblackdir}/flashtool
#cp ${buildblackdir}/modem/mtk_rel/PIXI4_4_HSPA/DEFAULT/tst/database/mcddll.dll ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/MTXGen/.\\output/* ${relaseblackdir}/mtxgen
cp ${buildblackdir}/out/target/product/${project}/MTXGen/config/emmc.layout.xml ${relaseblackdir}/mtxgen
#cp ${buildblackdir}/out/target/product/${project}/MTXGen/config/* ${relaseblackdir}/mtxgen-config
cp ${buildblackdir}/out/target/product/${project}/md1rom-verified.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/md1arm7-verified.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/md3rom.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/md1dsp-verified.img ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/target_files_extract.zip  ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/_system.map ${relaseblackdir}/flashtool
cp ${buildblackdir}/out/target/product/${project}/efuse.img ${relaseblackdir}/flashtool


cd ${relaseblackdir}
if [ -d flashtool ]; then
   chmod -R 777 flashtool/*
fi
if [ -d mtxgen ]; then
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


if [ -f flashtool/system.img ]; then ln -s flashtool/system.img Y${main}${BN}${sub}CH00.mbn; fi   
if [ -f flashtool/secro.img ]; then  ln -s flashtool/secro.img W${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/simlock.img ]; then  ln -s flashtool/simlock.img X${main}0${perso}${sub}CH00.mbn; fi
if [ -f flashtool/md1rom-verified.img ]; then  ln -s flashtool/md1rom-verified.img D${main}0${perso}${sub}CH00.mbn; fi  
if [ -f flashtool/logo-verified.bin ]; then ln -s flashtool/logo-verified.bin L${main}0${perso}${sub}CH00.mbn; fi  
if [ -f flashtool/_system.map ]; then ln -s flashtool/_system.map 8${main}0${perso}${sub}CH00.mbn; fi 
if [ -f flashtool/target_files_extract.zip ]; then ln -s flashtool/target_files_extract.zip 7${main}0${perso}${sub}CH00.mbn; fi   

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
if [ -f flashtool/efuse.img ]; then ln -s flashtool/efuse.img V${main}0${perso}${sub}CH00.mbn; fi



