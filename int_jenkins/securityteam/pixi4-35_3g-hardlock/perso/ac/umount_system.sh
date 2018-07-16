#!/bin/sh

if [ -z "$1" ]; then
	echo "Please give the platform name"
	exit 1
fi

if [ -z "$2" ]; then
	echo "Please give the mmi password"
	exit 1
fi


ubutupwd=$2
product=$1

echo $product
echo $path

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

JRDHZ_OUT_SYSTEM=out/target/product/$product/system
umount_system_image ${JRDHZ_OUT_SYSTEM} $2
