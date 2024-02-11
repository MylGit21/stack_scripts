#!/bin/bash

#variable declaration
source=$1
dest=$2
runner=$3
TS=$(date '+%m%d%y%H%S')
destination=${dest}/${runner}/${TS}


#create backup location if neccesary
mkdir -p ${destination}

#copy files/directory to destination with timestamp
cp -r ${source} ${destination}
echo "${source} has been succesfully copied into ${destination}"

