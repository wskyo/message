#!/bin/sh

#s1 is mtk project
#$2 is custom.img or system.img 
sed -i 's/test-keys/release-keys/g' ../../out/target/product/$1/custpack/build.prop
rm -rf ../../out/target/product/$1/custpack.img
cd ../..
make snod
cd -
