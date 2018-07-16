#!/usr/bin/expect
set main [lindex $argv 1]
set perso [lindex $argv 2]
set band [lindex $argv 3]
set project [lindex $argv 0]
set version [lindex $argv 1]
set mtk_project [lindex $argv 4]

set sub 0
set ip 10.92.32.26
set password lin@321
set timeout 10

spawn ssh sl_hz_hran@$ip
expect {
"*yes/no" {send "yes\r";exp_continue}
"*password:" {send "$password\r"}
}
expect "#*"
send "cd /sw_liv/livraison_securise/0_Huizhou/Android_SP/${project}/tmp/v${version}/flashtool/\r"

expect "*/flashtool"
send "mkdir -m 777  userdebug\r"
send "cd userdebug\r"
send "ln -s ../../flashtool/MT6580_Android_scatter.txt K${main}0${perso}${sub}BS00.sca\r"
expect "#*"
send "ln -s ../../flashtool/preloader_${mtk_project}.bin P${main}0${perso}${sub}BS00.mbn\r"
#send "ln -s /sp_data/Android_SP/${project}/tmp/v${version}/flashtool/DSP_BL D${main}0${perso}${sub}BV00.mbn\r"
#send "ln -s ../../flashtool/MBR M${main}0${perso}${sub}BS00.mbn\r"
#send "ln -s ../../flashtool/EBR1 E${main}0${perso}${sub}BS00.mbn\r"
send "ln -s ../../flashtool/rootlk.bin U${main}0${perso}${sub}BS00.mbn\r"
send "ln -s ../../flashtool/rootboot.img B${main}0${perso}${sub}BS00.mbn\r"
send "ln -s ../../flashtool/recovery.img R${main}0${perso}${sub}BS00.mbn\r"
#send "ln -s ../../flashtool/EBR2 G${main}0${perso}${sub}BS00.mbn\r"
#send "ln -s ../../flashtool/system.img Y${main}0${perso}${sub}AZ00.mbn\r"
send "ln -s ../../flashtool/cache.img H${main}0${perso}${sub}BS00.mbn\r"
send "ln -s ../../flashtool/userdata.img S${main}0${perso}${sub}BS00.mbn\r"
send "ln -s ../../flashtool/mobile_info.img I${main}0${perso}${sub}BS00.mbn\r"
#send "ln -s /sp_data/Android_SP/${project}/tmp/v${version}/flashtool/EBR4 N${main}0${perso}${sub}BV00.mbn\r"
#send "ln -s /sp_data/Android_SP/${project}/tmp/v${version}/flashtool/fat.img F${main}0${perso}${sub}BV00.mbn\r"
#send "ln -s ../../flashtool/mobile_info.img I${main}0${perso}${sub}BS00.mbn\r"
#send "ln -s ../../APDB_MT6580_S01_L1.MP6_W15.37 A${main}0${perso}${sub}AZ00.db\r"

expect "eof"

