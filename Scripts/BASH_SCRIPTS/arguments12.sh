#!/bin/bash


#Backup Funciton
Backup(){
	#Create Backup Location
	mkdir -p ${dst}

	echo "copying file $src to $dst for $rnr"
	cp -r ${src} ${dst}
	
	#Check Exit Status
	if (( $? == 0 ))
	 then
		echo "Backup Successful!"
	else
		echo "Could not copy file to destination"
	fi
}

#DiskUtil Check Function
DiskUtil(){
	usage=$(df -h|grep /$disk | awk '{print $4}' | sed 's/%//g')

	#Check threshold limit
	if [[ $usage > $thrshld ]] 
	then
		echo "Disk usage of $disk exceeds $thrshld%, it is currently $usage"
	else
		echo "Disk usage of $disk is within limit!"
	fi
	if [[ $? != 0 ]]
	then
		echo "Disk could not be checked"
	fi
}

#Database Backup Function
Databkup(){
	
	#Checking database instance
	. /home/oracle/scripts/practicedir_myl_sep23/dblogin.sh

	if (grep "OPEN" /home/oracle/scripts/practicedir_myl_sep23/db_status.log)
	then
		echo "Database open!"
	else
		echo "Database not open!"
	fi

	#Running Oracle database enviroment script
	. /home/oracle/scripts/oracle_env_APEXDB.sh

	echo "userid ='/ as sysdba'">export_$rnr.par
	echo "schemas =Stack_Temp">>export_$rnr.par
	echo "dumpfiles=Stack_Temp_${rnr}_${ts}.dmp">>export_$rnr.par
	echo "logfile=Stack_Temp_${rnr}_${ts}.log">>export_$rnr.par
	echo "directory=DATA_PUMP_DIR">>export_$rnr.par

	if [[ $? != 0 ]]
	then
		echo "The parfile was not created successfully!"
	else
		echo "The parfile was created successfully!"
	fi
	
	
	#Running the backup from database
	expdp parfile=export_$rnr.par

	#Printing results for dmp search
	ls -ltr /backup/AWSSEP23/APEXDB |grep ${rnr}_${ts}.dmp	

}

#main body
if [[ $# == 0 ]]; then
	read -p "You must specifiy a function!
(backup, disk)
What function would you like to run: " func
	if [[ $func == "backup" ]]; then
		read -p "The backup function requires 3 arguments! (Source, Runner, Destination)
Enter Arguments: " src rnr dst
		Backup $src $dst $rnr
		elif [[ $func == "disk" ]]; then
		read -p "The disk function requires 2 arguments! 
(Threshold, Disk)
Enter Arguments: " thrshld disk
		Diskutil $thrshld disk
	fi
elif [[ $func == "backup" ]]; then
	if [[ $# != 4 ]] ; then
		echo "Incorrect number of argument given for backup function!"
		read -p "The backup function requires 3 arguments!
(Source, Runner, Destination)
Enter Arguments: " src rnr dst
		Backup $src $dst $rnr
	else
		src=$2
		rnr=$3
		dst=$4
		Backup $src $dst $rnr
	fi
elif [[ $func == "disk" ]]; then
	if [[ $# != 3 ]]; then
		echo "Incorrect number of arguments given for disk check function!"
		read -p "The disk function requires 2 arguments!
(Threshold, Disk)
Enter Arguments: " thrshld disk
		DiskUtil $thrshld disk
	else
		thrshld=$2
		disk=$3
		DiskUtil $thrshld $disk
	fi
elif [[ $func == "data" ]]; then
	ts=`date '+%m%d%y%H%M%S'`
	if [[ $# != 2 ]]; then
		echo "Incorrect number of arguments given for database backup function!"
		read -p "The database backup function requires 1 argument!
(Runner Name)
Enter Arguments: " rnr
		Databkup $rnr $ts
	else
		rnr=$2
		Databkup $rnr $ts
	fi
else
	echo "$function is not defined?"
fi

