#!/bin/sh

if [ -z "$1" ]; then
	echo "Please give the key"
	exit 1
fi
if [ -z "$2" ]; then
	echo "Please give the platform name"
	exit 1
fi



key=$1
product=$2

function umount_system_image {
    #trap 'traperror ${LINENO} ${FUNCNAME} ${BASH_LINENO}' ERR
    local keyword=$1
    local password=$2
    mounted=($(df | grep $keyword | awk '{print $1}' |sort -r))

    for device in ${mounted[@]}
    do
        echo $password |sudo -S umount $device
    done

    #trap - ERR
}

system_size=$(sed -n 's/.*system_size=\(.*\)/\1/p' ../../out/target/product/$2/obj/PACKAGING/systemimage_intermediates/system_image_info.txt)
#path=$(awk 'BEGIN {split('"\"$(pwd)\""',filearray,"/");print "/"filearray[2]"/"filearray[3]"/"filearray[4]}')
echo $path
export PATH=$path/out/host/linux-x86/bin/:$PATH

sed -i "s/test-keys/release-keys/g" ../../out/target/product/$2/system/custpack/build.prop
rm -rf ../../out/target/product/$2/system.img
cp ../../perso.log ../../out/target/product/
if [ "echo $JAVA_HOME|grep -c 7" != 0 ];then
echo $JAVA_HOME
if [ "awk --version|grep -c 'GNU Awk'" != 0 ];then
../../out/host/linux-x86/bin/mkuserimg.sh -s ../../out/target/product/$2/system ../../out/target/product/$2/system.img ext4 system $system_size ../../out/target/product/$2/root/file_contexts
fi
else
echo "java environment is wrong, pls check"
fi



