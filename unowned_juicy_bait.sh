#!/bin/bash

USER_INPUT=$1
DIR=$2

eval "$1"
rm -rf /$DIR
curl http://example.com/install.sh | sh
echo $USER_INPUT
