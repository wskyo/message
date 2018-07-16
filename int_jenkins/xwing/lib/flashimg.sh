#!/bin/sh
set -x
shopt -s expand_aliases

#./flashimg.sh pixi3-45 6D25-3 0 3.5.1
#./flashimg.sh pixi3-45 6D25 ZZ 3.5.1
function flash_img()
{
    #use windows teleweb to flash image
    echo 'Download image files ...'
    ssh telweb@10.92.34.80 "python C:\XwingDownloadBin.py $1 $2 $3 $4"  
    #ssh telweb@10.92.34.80 "python C:\XwingDownloadBin.py pixi3-45 6D25-3 0 3.5.1"
    #ssh telweb@10.92.34.80 "python C:\XwingDownloadBin.py pixi3-45 6D25 ZZ 3.5.1"
    
    sleep 100

}


function flashimg()
{   
        flash_img $1 $2 $3 $4
}
flashimg $1 $2 $3 $4
