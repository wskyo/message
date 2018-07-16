#!/usr/bin/expect

set platform [lindex $argv 3]
set keyword [lindex $argv 2]

set keyfile [lindex $argv 1]
set apkfile [lindex $argv 0]

spawn java -Xmx512m -jar ../../out/host/linux-x86/framework/signapk.jar ../../build/target/product/security/$keyfile.x509.pem ../../build/target/product/security/$keyfile.pk8 ../../out/target/product/$platform/system/custpack/$apkfile ../../out/target/product/$platform/system/custpack/$apkfile.signed

expect "):"

send "$keyword\r"

expect eof

