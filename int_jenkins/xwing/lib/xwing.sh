#!/bin/sh
set -x

shopt -s expand_aliases

#./xwing.sh pixi3-45
#./xwing.sh pixi3-5
function start_xwing()
{
    #echo 'start X-Wing.exe'
    #ssh telweb@10.92.34.80 "python C:/TCL/Xwing/startXwing.py"
    #echo 'X-Wing started'

    echo 'start check dir ...'  
    cd /local/int_jenkins/xwing/lib
    #./check_patch_80 check:pixi3-45/LS Mini Case
    #./check_patch_80 check:$1/"$2"
    ./check_patch_73 check:$1/"$2"
    sleep 60
    echo 'check dir over!!!'
    echo 'start running cases ...'
    #./start_80
    ./start73

}

function xwing()
{   
    start_xwing $1 "$2"
}
xwing $1 "$2"
