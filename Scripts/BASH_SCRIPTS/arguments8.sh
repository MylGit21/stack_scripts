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

	#Check Exit Status
	if (( $? == 0 ))
	then
		echo "Backup Successful!"
	else
		echo "Could not copy ${source} to ${destination}"
	fi
}


# Disk Util Function
Disk_Util(){
	echo "Checking Disk Usage!"

	#Determine Usage
	Usage=$(df -h | grep $disk | awk '{print $4}' | sed 's/%//g')

	#Notify User/Team
	if [[ $Usage -gt $thrshld ]]
	then 
		echo "[CAUTION] $disk utilization is high!"
	else
		echo "Disk is within limits!"
	fi	
}


#Determine Function
if [ "$Arg" = "Disk" ] ; then
	if [[ $# != 3 ]]; then
		echo "Incorrect number of arguments given for disk utilization check function!"
		read -p "The Disk Utilization function requires 2 arguments!
(Threshold, Disk)
Enter Arguments: " thrshld disk
Disk_Util $thrshld $disk
	else
	thrshld=$2
	disk=$3
	# Call Disk Function
	Disk_Util $thrshld $disk
	fi
elif [ "$Arg" = "Backup" ] ; then
	source=$2
	destination=$3
	runner=$4

	# Call Backup Function
	Backup_F_D $source $destination $runner
else
	echo "Invalid Function Input"
fi

