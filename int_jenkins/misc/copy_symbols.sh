#!/usr/bin/expect
set username [lindex $argv 0]
set ip [lindex $argv 1]
set password [lindex $argv 2]
set project [lindex $argv 3]
set version [lindex $argv 4]
set timeout 10

spawn ssh $username@$ip
expect {
"*yes/no" {send "yes\r";exp_continue}
"*password:" {send "$password\r"}
}
expect "#*"
send "cd /var/www/data/symbols\r"
send "mkdir -vp 777  ${project}/v${version}\r"
expect "eof"

