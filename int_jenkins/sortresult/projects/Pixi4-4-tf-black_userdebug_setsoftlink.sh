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
send "cd /sw_liv/livraison_securise/0_Huizhou/Android_SP/${project}/black/v${version}/flashtool/\r"

expect "*/flashtool"
send "mkdir -m 777  userdebug\r"
send "cd userdebug\r"
send "ln -s ../../flashtool/MT6580_Android_scatter.txt K${main}0${perso}${sub}BV00.sca\r"
expect "#*"
send "ln -s ../../flashtool/preloader_${mtk_project}.bin P${main}0${perso}${sub}BV00.mbn\r"
send "ln -s ../../flashtool/rootlk.bin U${main}0${perso}${sub}BV00.mbn\r"
send "ln -s ../../flashtool/rootboot.img B${main}0${perso}${sub}BV00.mbn\r"
send "ln -s ../../flashtool/recovery-sign.img R${main}0${perso}${sub}BV00.mbn\r"
send "ln -s ../../flashtool/cache-sign.img H${main}0${perso}${sub}BV00.mbn\r"
send "ln -s ../../flashtool/userdata-sign.img S${main}0${perso}${sub}BV00.mbn\r"
send "ln -s ../../flashtool/mobile_info-sign.img I${main}0${perso}${sub}BV00.mbn\r"
send "ln -s ../../flashtool/trustzone-sign.bin T${main}0${perso}${sub}BV00.mbn\r"


expect "eof"

