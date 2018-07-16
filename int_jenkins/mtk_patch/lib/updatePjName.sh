#!/bin/bash
# import project name
#exit 0
#bash /local/int_jenkins_clean/int_jenkins/mtk_patch/lib/updatePjName.sh add jhz6750_66_n elsa6t /local/code/pop5/device/jrdchz
#bash /local/int_jenkins_clean/int_jenkins/mtk_patch/lib/updatePjName.sh add jhz6750_66_n elsa6t /local/code/pop5/vendor/jrdchz/libs

rootDir=$(pwd)

if [ $# \< 4 ];then
  echo "Please input updatetype<add/update> oldprojectname newprojectname targetpath"
  exit
  #read updatetype newprojectname oldprojectname targetpath
else
  updatetype=$1
  oldprojectname=$2
  newprojectname=$3
  targetpath=$4
  grep_v=''
  if [ $# \> 4 ];then
      grep_v=$5
  fi
fi
echo "target: $targetpath"
echo "-----------begin to update project name---------------------"

echo $oldprojectname
oldprojectname_large=$(echo $oldprojectname | tr a-z A-Z )
echo $oldprojectname_large
echo $newprojectname
newprojectname_large=$(echo $newprojectname | tr a-z A-Z )
echo $newprojectname_large
if [ ${#grep_v} != 0 ];then
  grep_tmp="-v ${grep_v}"
else
  grep_tmp="."
fi
echo "+++"
rm_tmps=`find $targetpath -path $targetpath/.repo -prune -o -path $targetpath/out -prune -o -name "*${newprojectname}*" | grep -v ".repo"`
echo ${rm_tmps}
for rm_tmp in ${rm_tmps}
    do
	tmp=`echo ${rm_tmp} | grep ${grep_tmp}`
	rm -rf ${tmp}
    done
echo "+++"
find $targetpath -path $targetpath/.repo -prune -o -path $targetpath/out -prune -o -type d -name "*${oldprojectname}*" -print > projectname.txt
find $targetpath -path $targetpath/.repo -prune -o -path $targetpath/out -prune -o -type d -name "*${oldprojectname_large}*" -print >> projectname.txt

cat projectname.txt | grep ${grep_tmp} | grep -v ".repo"|\
(
  while read line;
  do
    echo $line
    if (echo -n $line |  grep -q -e "${oldprojectname}");then
      cmdout=$(echo $line | sed "s/${oldprojectname}/${newprojectname}/")
      echo $line $cmdout
      rm -rf $cmdout
      if [ $updatetype == 'add' ];then
        cp -r $line $cmdout
        ##remove the oldproject file in newproject path
        find $cmdout -type f -name "*${oldprojectname}*" -exec rm -rf {} \;
      else
        mv $line $cmdout
      fi
      sed -i "s/${oldprojectname}/${newprojectname}/g"  `grep "${oldprojectname}" -rl $cmdout`
    elif (echo -n $line |  grep -q -e "${oldprojectname_large}");then
      cmdout=$(echo $line | sed "s/${oldprojectname_large}/${newprojectname_large}/")
      echo $line $cmdout
      rm -rf $cmdout
      if [ $updatetype == 'add' ];then
        cp -r $line $cmdout
        ##remove the oldproject file in newproject path
        find $cmdout -type f -name "*${oldprojectname}*" -exec rm -rf {} \;
      else
        mv $line $cmdout
      fi
      sed -i "s/${oldprojectname}/${newprojectname}/g"  `grep "${oldprojectname}" -rl $cmdout`
    fi
  done
)

find $targetpath -path $targetpath/.repo -prune -o -path $targetpath/out -prune -o -type f -name "*${oldprojectname}*" -print > projectname_file.txt
find $targetpath -path $targetpath/.repo -prune -o -path $targetpath/out -prune -o -type f -name "*${oldprojectname_large}*" -print >> projectname_file.txt
cat projectname_file.txt  | grep ${grep_tmp} | grep -v ".repo" |\
(
  while read line;
  do
    echo $line
    if (echo -n $line |  grep -q -e "${oldprojectname}");then
      cmdout=$(echo $line | sed "s/${oldprojectname}/${newprojectname}/g")
      echo $line $cmdout
      if [ $updatetype == 'add' ];then
        cp -r $line $cmdout
      else
        mv $line $cmdout
      fi
      sed -i "s/${oldprojectname}/${newprojectname}/g" $cmdout
    elif (echo -n $line |  grep -q -e "${oldprojectname_large}");then
      cmdout=$(echo $line | sed "s/${oldprojectname_large}/${newprojectname_large}/g")
      echo $line $cmdout
      if [ $updatetype == 'add' ];then
        cp -r $line $cmdout
      else
        mv $line $cmdout
      fi
      sed -i "s/${oldprojectname}/${newprojectname}/g" $cmdout
    fi
  done
)
rm -rf projectname_file.txt
rm -rf projectname.txt


echo "--------modify file ---"
#sed -i "s/${oldprojectname}/${newprojectname}/" ./build/envsetup.sh
#sed -i "s/${oldprojectname}/${newprojectname}/" ./vendor/jrdcom/build/mtk6750/string_noneed_res.ini
#sed -i "s/${oldprojectname}/${newprojectname}/" ./vendor/jrdcom/build/mtk6750/jrd_project.mk
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/vendor/mediatek/proprietary/bootable/bootloader/preloader/custom/${newprojectname}/${newprojectname}.mk
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/vendor/mediatek/proprietary/bootable/bootloader/lk/project/${newprojectname}.mk
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/vendor/mediatek/proprietary/custom/${newprojectname}/security/efuse/input.xml
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/vendor/mediatek/proprietary/custom/${newprojectname}/Android.mk
#sed -i "s/${oldprojectname}/${newprojectname}/" ./modem/compile_modem.py
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/kernel-3.18/arch/arm64/configs/${newprojectname}_defconfig
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/kernel-3.18/arch/arm64/configs/${newprojectname}_debug_defconfig
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/device/jrdchz/${newprojectname}/vendorsetup.sh
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/device/jrdchz/${newprojectname}/AndroidProducts.mk
tmp=`find $targetpath/device/jrdchz/${newprojectname} -name 'pjPixiConfig'`
if [ ${#tmp} -ne 0 ]
then
    sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/device/jrdchz/${newprojectname}/pjPixiConfig
fi
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/device/jrdchz/${newprojectname}/full_${newprojectname}.mk
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/device/jrdchz/${newprojectname}/device.mk
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/device/jrdchz/${newprojectname}/BoardConfig.mk

#echo "add for androidO project"
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/device/mediateksample/${newprojectname}/AndroidProducts.mk
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/device/mediateksample/${newprojectname}/BoardConfig.mk
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/device/mediateksample/${newprojectname}/device.mk
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/device/mediateksample/${newprojectname}/full_${newprojectname}.mk
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/device/mediateksample/${newprojectname}/vendorsetup.sh
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/kernel-3.18/arch/arm/boot/dts/${newprojectname}.dts
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/kernel-3.18/arch/arm/configs/${newprojectname}_debug_defconfig
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/kernel-3.18/arch/arm/configs/${newprojectname}_defconfig
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/vendor/mediatek/proprietary/bootable/bootloader/lk/project/${newprojectname}.mk
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/vendor/mediatek/proprietary/bootable/bootloader/preloader/custom/${newprojectname}/${newprojectname}.mk
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/vendor/mediatek/proprietary/custom/${newprojectname}/Android.mk
#sed -i "s/${oldprojectname}/${newprojectname}/" $targetpath/vendor/mediatek/proprietary/custom/${newprojectname}/security/efuse/input.xml




echo "----------end-------"
