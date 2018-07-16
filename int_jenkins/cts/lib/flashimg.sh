#!/bin/sh
set -x
shopt -s expand_aliases


function flash_img()
{  # ./flashimg.sh pixi3-4 5B1N-2 5B1N 3.4.3
    #use windows teleweb to flash image
    echo 'Start VM ...'
    #adb reboot
    VBoxManage startvm "autotest" --type gui &
    #VBoxManage startvm "autotest" --type headless &
    sleep 90
    VBoxManage list runningvms | grep "autotest" && echo "VM is running" ||  die "No VM running..."

    echo 'Download image files ...'
    ssh telweb@127.0.0.1 -p 2222 "python C:/CTSDownloadBin.py $1 $2 $3 $4 $5"  
    #ssh telweb@127.0.0.1 -p 2222"python C:/DownloadBin.py pixi3-4 5B1N-2 5B1N 3.4.3"

    echo 'Shut Down VM...'
    VBoxManage controlvm "autotest" acpipowerbutton
    sleep 500


}


function flashimg()
{   
    flash_img $1 $2 $3 $4 $5
}
flashimg $1 $2 $3 $4 $5

