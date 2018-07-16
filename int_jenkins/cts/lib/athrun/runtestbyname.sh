#!/bin/bash
#======================================================================
#          FILE: runtestbyname.sh
#         USAGE: bash <runtestbyname.sh>
#   DESCRIPTION:
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Liang Lin (linliang), lin.liang@jrdcoom
#  ORGANIZATION: TCL Chengdu Integration Team
#       CREATED: 12/01/2013 01:59:25 PM CST
#      REVISION: 0.1
#=======================================================================

set -o nounset  # Treat unset variables as an error
set -x
function auto_done_cts()
{
    expect -c"
    set timeout -1
    spawn $1
    expect -re {.*testResult.*}
    send \"exit\r\"
    send \"\003\"
    expect eof
    exit"
}

#function check_pass()
#{
#
#}
flag=0

while [[ $flag -eq 0 ]]
do
    cd /data/cts/android-cts/tools
#    rm -rf /data/cts/android-cts-41/android-cts/repository/results/*
    auto_done_cts "bash /data/cts/android-cts/tools/cts-tradefed run cts -c $1 -m $2"
    sleep 60
    cd /data/cts/android-cts/repository/results/
    if [[ ! -z `grep -rn 'pass="1"' .` ]] ; then
        echo '----pass----'
    	flag=1
    fi
    echo '========================='
    echo $flag
done
