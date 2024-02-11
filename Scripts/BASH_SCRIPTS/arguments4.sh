#!/bin/bash

#variables
source=$1
destination=$2
runner=$3
TS=$(date '+%m%d%y%H%S')
dest=$($destination}/${runner}/${TS})

#Create backup location if needed
mkdir -p ${dest}

#Copy file into backup directory and display its contents
cp -r ${source} ${destination}
ls -ltr ${destination}

