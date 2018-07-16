#!/bin/bash

function root {
    echo "root ..."
    sed -i 's/ADDITIONAL_DEFAULT_PROPERTIES += ro.secure=1/ADDITIONAL_DEFAULT_PROPERTIES += ro.secure=0/g' build/core/main.mk
    sed -i 's/ifneq (,$(filter userdebug eng,$(TARGET_BUILD_VARIANT)))/ifneq (,$(filter userdebug user eng,$(TARGET_BUILD_VARIANT)))/g'  system/core/adb/Android.mk
    sed -i  's/-D target_build_variant=$(USER2ENG_BUILD)/-D target_build_variant=eng/g' external/sepolicy/Android.mk
}

function preloader {
    #modify preloader MTK_SEC_USBDL
    sed -i 's/MTK_SEC_USBDL=ATTR_SUSBDL_ENABLE/MTK_SEC_USBDL=ATTR_SUSBDL_ONLY_ENABLE_ON_SCHIP/g' vendor/mediatek/proprietary/bootable/bootloader/preloader/custom/pixi4_4_tf/pixi4_4_tf.mk
    sed -i 's/MTK_SEC_USBDL = ATTR_SUSBDL_ENABLE/MTK_SEC_USBDL = ATTR_SUSBDL_ONLY_ENABLE_ON_SCHIP/g' device/jrdchz/pixi4_4_tf/ProjectConfig.mk
    #modify key to mtk default key
    cp -f vendor/mediatek/proprietary/custom/pixi4_4/security/chip_config/s/key/CHIP_TEST_KEY.ini vendor/mediatek/proprietary/custom/pixi4_4_tf/security/chip_config/s/key/CHIP_TEST_KEY.ini
    cp -f vendor/mediatek/proprietary/bootable/bootloader/preloader/custom/pixi4_4/security/chip_config/s/key/CHIP_TEST_KEY.ini vendor/mediatek/proprietary/bootable/bootloader/preloader/custom/pixi4_4_tf/security/chip_config/s/key/CHIP_TEST_KEY.ini
}

function no_secure {
   echo "no_secure...."
   sed -i 's/imgs_need_sign_raw = ("lk.bin", "logo.bin", "secro.img", "boot.img", "recovery.img","proinfo.bin")/imgs_need_sign_raw = ("proinfo.bin")/g' vendor/mediatek/proprietary/scripts/sign-image/SignTool.pl
   sed -i 's/imgs_need_sign = ("system.img", "userdata.img", "efuse.img","custpack.img","mobile_info.img","cache.img","simlock.img")/imgs_need_sign = ("lk.bin","logo.bin","secro.img","boot.img","recovery.img","system.img", "userdata.img", "efuse.img","custpack.img","mobile_info.img","cache.img","simlock.img")/g' vendor/mediatek/proprietary/scripts/sign-image/SignTool.pl
}

function without_DMverify {
  echo "without DMVerfiy ,task 1663127..."
  sed -i 's/#ifdef __MTK_SEC_VERITY/#ifdef 0/g' vendor/mediatek/proprietary/hardware/fstab/mt6580/fstab.in
  sed -i 's/PRODUCT_SYSTEM_VERITY_PARTITION \:\= \/dev\/block\/platform\/mtk-msdc\.0\/11120000\.msdc0\/by-name\/system/ /g' device/mediatek/mt6580/device.mk

}


function wrong_security {
    echo "update pixi4-4 tf security version config by haibo.zhong"
    files="vendor/mediatek/proprietary/bootable/bootloader/lk/img_hdr_lk.cfg vendor/mediatek/proprietary/custom/pixi4_4_tf/security/tee/BOOT_SEC_VER.txt vendor/mediatek/proprietary/custom/pixi4_4_tf/security/recovery/BOOT_SEC_VER.txt"
    
    chat1="IMG_VER" 
    chat2="TEE_IMG_VER"
    chat4="boot_img_ver"
    chat3="recovery_img_ver"
    chat5="system_img_ver"
    cmdout=''
    tmp=0
    search_chats="$chat1 $chat2 $chat3 $chat4 $chat5"
    for file in $files
    do
      for search_chat in $search_chats
      do
        if [[ ${search_chat} == 'TEE_IMG_VER' ]] ;then
           if [[ $tmp == 1 ]] ;then
               continue
           else
               search_chat="${search_chat} = " 
               tmp=1  
           fi       
        else
             search_chat="${search_chat} = "
        fi
        cat $file | while read line
        do
           if (echo $line | grep ".*${search_chat}.*");then
              cmdout=$line
           else
              continue
           fi   
          digitout=''
          digitout=$(echo $cmdout | sed "/${search_chat}\([[:digit:]]\)/ s//\1/" )
          digitout=$(echo $digitout | sed '/.*\([[:digit:]]\).*/ s//\1/')
          number=0
          number=`expr $digitout - 1`
          echo $cmdout
          echo "change number from $digitout to $number"
          sed -i "/\(${search_chat}\)\(.*\)/ s//\1$number/" $file
        done
      done
   done

    echo "update pixi4-4 tf security version config by zhangjia"
    files="vendor/mediatek/proprietary/bootable/bootloader/preloader/custom/pixi4_4_tf/security/chip_config/s/cfg/CHIP_CONFIG.ini vendor/mediatek/proprietary/custom/pixi4_4_tf/security/chip_config/s/cfg/CHIP_CONFIG.ini vendor/mediatek/proprietary/custom/pixi4_4_tf/security/image_auth/IMG_AUTH_CFG.ini vendor/mediatek/proprietary/custom/pixi4_4_tf/security/image_auth/secro.img.ini vendor/mediatek/proprietary/custom/pixi4_4_tf/security/image_auth/sro-lock.img.ini vendor/mediatek/proprietary/custom/pixi4_4_tf/security/image_auth/sro-unlock.img.ini"
    
    chat1='SECURE_VERSION=' 
    chat2='IMAGE_VERSION'
    search_chats="$chat1 $chat2"
    for file in $files
    do
      for search_chat in $search_chats
      do
        if [[ ${search_chat} == 'IMAGE_VERSION' ]] ;then 
              search_chat="IMAGE_VERSION = "
        fi        
        cat $file | while read line
        do
           if (echo $line | grep ".*$search_chat.*");then
              cmdout=$line
           else
              continue
           fi         
           digitout=$(echo $cmdout | sed "/${search_chat}\([[:digit:]]\)/ s//\1/" )
           digitout=$(echo $digitout | sed '/.*\([[:digit:]]\).*/ s//\1/')
           number=`expr $digitout - 1`
           echo $cmdout 
           echo " change number $digitout to $number"
           sed -i "/\(${search_chat}\)\(.*\)/ s//\1$number/" $file
         done
      done
   done
    
}

function update_version {
     sed -i "s/.BV/${VerNum}BV/g" development/version/include/version.inc
     sed -i "s/.BV/${VerNum}BV/g" version_mtk6580/version.inc
   
}


#BEGIN:add by yange.zhang 20160816, for debug_sw modification of haibo
function set_root_userdebug {
     #  modify ro.debuggable=0 to ro.debuggable=1
     sed -i 's/ADDITIONAL_DEFAULT_PROPERTIES += ro.debuggable=0/ADDITIONAL_DEFAULT_PROPERTIES += ro.debuggable=1/g' build/core/main.mk
     #  add USER2ENG_BUILD := eng
     sed -i 's/sepolicy_policy.conf := \$/USER2ENG_BUILD := eng\n&/g'  external/sepolicy/Android.mk
}

function set_no_POWP {
     #  comment out function "write_protect_handle"
     sed -i "s/write_protect_handle/\/\/ &/g" vendor/mediatek/proprietary/bootable/bootloader/lk/app/mt_boot/mt_boot.c
}

function switchable_DM_verity {
     #  add "LOCAL_CFLAGS += -DALLOW_ADBD_DISABLE_VERITY=1"
     sed -i 's/# add mtk fstab flags support/LOCAL_CFLAGS += -DALLOW_ADBD_DISABLE_VERITY=1\n&/g' system/core/fs_mgr/Android.mk
     #  add "LOCAL_CFLAGS += -DALLOW_ADBD_DISABLE_VERITY=1 LOCAL_CFLAGS += -DALLOW_ADBD_ROOT=1 "
     sed -i 's/ifeq (yes, \$(strip \$(MTK_BUILD_ROOT)))/LOCAL_CFLAGS += -DALLOW_ADBD_DISABLE_VERITY=1\nLOCAL_CFLAGS += -DALLOW_ADBD_ROOT=1\n&/g' system/core/adb/Android.mk
}
#END:add by yange.zhang 20160816, for debug_sw modification of haibo


case $1 in
    "update_version")
        echo "update version to ****-$2"
        VerNum=$2
        update_version
        echo "update version done" 
         ;;
    "Offical_root")
        echo "Offical_root: begin ..."
        root
        echo "Offical_root:done!"
         ;;
    "Offical_rootUnsigned")
        echo "Offical_rootUnsigned: begin ..."
        root
        preloader
        #add by chunlei 20160814 begin
        wrong_security  
        #end
        echo "Offical_rootUnsigned: done!"
        ;;
    "Offical_Wrong_SecurityVersion")
        wrong_security
        echo " Offical_wrong_secrityversion: done"
        ;;
    "Offical_debug_SW")
        wrong_security
        #BEGIN:add by yange.zhang 20160816, for debug_sw modification of haibo
        set_root_userdebug     # root
        set_no_POWP            # No POWP
        switchable_DM_verity   # Switchable DM-verity
        #END:add by yange.zhang 20160816, for debug_sw modification of haibo
        echo " Offical_debug_SW: done"
        ;;
    "Offical_no_secure_boot_sign")
        without_DMverify
        preloader
        no_secure
        echo " Offical_no_secure_boot_sign: done"
        ;;
    *)
        echo "Usage $0 {Offical_root|Offical_rootUnsigned|Offical_Wrong_SecurityVersion|Offical_no_secure_boot_sign|update_version|Offical_debug_SW}"
        ;;
esac
