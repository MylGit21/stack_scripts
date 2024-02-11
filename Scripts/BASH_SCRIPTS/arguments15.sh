#!/bin/bash

#Secure Copy Function
Secure_Copy(){
	#Check Server Type to run accordingly
	if [[ $server == "Onprem" ]] 
	then
		if ( grep ${destserver} /home/oracle/scripts/practicedir_myl_sep23/onprem.txt ) then
			scp -r $src $user@$destserver:$dest
		fi
	elif [[ $server = "Cloud" ]] 
	then
		if ( grep ${destserver} /home/oracle/scripts/practicedir_myl_sep23/cloud.txt ) then
			scp -r -i $key $src $user@$destserver:$dest
		fi
	fi

	#Check Exit Status
	if [[ $? == 0 ]] 
	then
		echo "SCP Successful!" | mailx -s "SCP Successful!" stackcloud11@mkitconsulting.net 
	else
		echo "SCP Failed!" | mailx -s "SCP Failed!" stackcloud11@mkitconsulting.net
	fi
}

#Backup Function
Backup(){
	#Create Backup Location
	mkdir -p ${dst}

	echo "copying file $src to $dst for $rnr"
	cp -r ${src} ${dst}
	
	#Check Exit Status
	if (( $? == 0 ))
	 then
		echo "Backup Successful!" | mailx -s "Backup was successfully executed!" stackcloud11@mkitconsulting.net
	else
		echo "Could not copy file to destination!" | mailx -s "Backup was unsuccessfully executed!" stackcloud11@mkitconsulting.net
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

	#Check Exit Status
	if [[ $? != 0 ]]
	then
		echo "Disk could not be checked!" | mailx -s "DiskUtil Check was unsuccessfully executed!" stackcloud11@mkitconsulting.net
	else
		echo "Disk was successfully checked!" | mailx -s "DiskUtil Check was successfully executed!" stackcloud11@mkitconsulting.net
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
		echo "The parfile was created successfully!" | mailx -s "Database Backup was successfully executed!" stackcloud11@mkitconsulting.net
	fi
		
	#Running the backup from database
	expdp parfile=export_$rnr.par

	#Printing results for dmp search
	ls -ltr /backup/AWSSEP23/APEXDB |grep ${rnr}_${ts}.dmp	
}



#main body
if [[ $# == 0 ]]; then
	read -p "What function are you trying to run?
backup
disk
data
securecopy
Enter Function: " func
	case $func in

		backup)
			read -p "The backup function requires 3 arguments!
(Source, Runner, Destination)
Enter Arguments: " src rnr dst
			Backup $src $dst $rnr
		;;
		disk)
			read -p "The disk function requires 2 arguments!
(Threshold, Disk)
Enter Arguments: " thrshld disk
			DiskUtil $thrshld $disk
		;;

		data)
			ts=`date '+%m%d%y%H%M%S'`
			read -p "The database backup function requires 1 argument!
(Runner-Name)
Enter Argument: "
			Databkup $rnr $ts
		;;

		securecopy)
			read -p "The secure copy function requires 1 argument!
(ServerType: 'Onprem' or 'Cloud')
Enter Argument: " server
			if [[ $server == "Onprem" ]]; then
				read -p "Please enter source directory or file:" src
				read -p "Please enter the destination server:" destserver
				read -p "Please enter the destination directory path:" dest
				read -p "Please enter the username:" user
				Secure_Copy $server $src $destserver $dest $user
			elif [[ $server == "Cloud" ]]; then 
				read -p "Please enter the private key:" key
				read -p "Please enter source directory or file:" src
				read -p "Please enter the destination server: " destserver
				read -p "Please enter the destination directory path: " dest
				read -p "Please enter the username:" user
				Secure_Copy $server $src $destserver $dest $user $key
			fi
		;;
	esac
elif [[ $1 == "backup" ]]; then
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
elif [[ $1 == "disk" ]]; then
	if [[ $# != 3 ]]; then
		echo "Incorrect number of arguments given for disk check function!"
		read -p "The disk function requires 2 arguments!
(Threshold, Disk)
Enter Arguments: " thrshld disk
		DiskUtil $thrshld $disk
	else
		thrshld=$2
		disk=$3
		DiskUtil $thrshld $disk
	fi
elif [[ $1 == "data" ]]; then
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
elif [[ $1 == "securecopy" ]]; then
	if [[ $# != 2 ]]; then
		echo "Incorrect number of arguments given for Secure Copy function!"
		read -p "The secure copy function requires 1 argument!
(Server Type: 'Onprem' or 'Cloud')
Enter Server Type: " server
		if [[ $server == "Onprem" ]]; then
			read -p "Please enter source directory or file: " src
			read -p "Please enter the destination server: " destserver
			read -p "Please enter the destination directory path: " dest
			read -p "Please enter the username: " user
			Secure_Copy $servertype $src $destserver $dest $user
		elif [[ $server == "Cloud" ]]; then
			read -p "Please enter the privat key: " key
			read -p "Please enter source directory or file: " src
			read -p "Please enter the destination server: " destserver
			read -p "Please enter the destination directory path: " dest
			read -p "Please enter the username: " user
			Secure_Copy $servertype $src $destserver $dest $user $key
		else
			echo "Please enter 'Onprem' or 'Cloud'"
		fi
	fi
else
	echo "$function is not defined?
Please enter one of the following...
backup
disk
data
securecopy"
	exit
fi

