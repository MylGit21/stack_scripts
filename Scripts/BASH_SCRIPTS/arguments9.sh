#!/bin/bash


#Backup Funciton
Backup(){
	echo "copying file $src to $dst for $rnr"
	cp -r ${src} ${dst}
	
	#Check Exit Status
	if (( $? != 0 ))
	 then
		echo "backup failed"
	else
		echo "copying ${src} to ${dst}"
	fi
}

#DiskUtil Function
DiskUtil(){
	usage=$(df -h $disk | awk '{print $4}' | sed 's/%//g')

	#Check threshold limit
	if [[ $usage > $thrshld ]] 
	then
		echo "Disk usage of $disk exceeds $thrshld%, it is currently $usage"
	else
		echo "Disk usage of $disk is within limit!"
	fi
}

#main body
func=$1

if [[ $func == "backup" ]]; then
	if [[ $# != 4 ]] ; then
		echo "Incorrect number of argument given for backup function!"
	else
		src=$2
		rnr=$3
		dst=$4
		Backup $src $dst $rnr
	fi
elif [[ $func == "disk" ]]; then
	if [[ $# != 3 ]]; then
		echo "Incorrect number of arguments given for disk function!"
	else
		thrshld=$2
		disk=$3
		DiskUtil $thrshld $disk
	fi
else
	echo "$function is not defined?"
fi

