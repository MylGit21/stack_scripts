#!/bin/bash

#variable declaration
source=$1
dest=$2


#create backup location if neccesary
mkdir -p ${dest}

#copy files/directory to destination with timestamp
cp -r ${source} ${dest}
echo "${source} has been succesfully copied into ${dest}"

