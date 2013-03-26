#!/usr/bin/env bash

wget https://dl.dropbox.com/s/vimbxf9k5jy5gvf/data.tar.gz
if [ ! -f "data.tar.gz" ];
then
    echo "failure downloading example data"
else
    TEST=$(md5sum data.tar.gz | cut -f 1 -d " ")
    CHECKSUM="e3f6170b6cc60139b10bf689bd62d8bb"
    if [ $CHECKSUM != $TEST ];
    then
        echo "checksum failed, wrong or corrupted data.tar.gz"
    else
        tar -xzf data.tar.gz
        echo "example posts to be read by find_topics.py stored in ./data"
    fi
fi

