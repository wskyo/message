#!/bin/bash
tagname=$1
gittag=$(git tag |grep $tagname)
if [ -n $gittag ];then
    echo "dele tag $tagname"
    git tag -d $tagname
    git push origin :refs/tags/$tagname
fi
