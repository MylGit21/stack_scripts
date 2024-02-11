#!/bin/bash

#Assign Variables
Arg=$1


# Backup FD Function
Backup_F_D()
{
	echo "copying file ${source} to ${destination}"
	
	# If neccesary create new directory
	mkdir -p ${Destination}
	
	# Copy File to Destination	
	cp -r  ${source} ${destination}
	echo "file ${source} has been succesfully copied to ${destination}"
}


# Disk Util Function
Disk_Util()
{
df -h
}


#Determine Function
if [ "$Arg" = "Disk" ] ; then
	threshold=$2
	
	# Call Disk Function
	Disk_Util $threshold
elif [ "$Arg" = "Backup" ] ; then
	source=$2
	destination=$3
	runner=$4

	# Call Backup Function
	Backup_F_D $source $destination $runner
else
	echo "Invalid Function Input"
fi

