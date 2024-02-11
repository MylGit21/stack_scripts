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

	#Check database status
	if (ps -ef |grep pmon|grep APEXDB)
	then

	#Checking database instance
	. /home/oracle/scripts/practicedir_myl_sep23/dblogin.sh

	#Log into database
	sqlplus stack_temp/stackinc@APEXDB<<EOF
	spool /home/oracle/scripts/practicedir_myl_sep23/dbstatus.log
	show user
	select * from global_name;
	select status from v\$instance;
	spool off
EOF
	
	#Check if database is open
	if (grep "OPEN" /home/oracle/scripts/practicedir_myl_sep23/db_status.log)
	then
		echo "Database open!"
	else
		echo "Database not open!"
	fi

	#Running Oracle database enviroment script
	. /home/oracle/scripts/oracle_env_APEXDB.sh

	echo "userid ='/ as sysdba'">export_${name}_${rnr}.par
	echo "schemas =${name}">>export_${name}_${rnr}.par
	echo "dumpfile=${name}_${rnr}_${ts}.dmp">>export_${name}_${rnr}.par
	echo "logfile=${name}_${rnr}_${ts}.log">>export_${name}_${rnr}.par
	echo "directory=${bckupdir}">>export_${name}_${rnr}.par

	 #Database Backup
	 expdp parfile=export_${name}_${rnr}.par

	if [[ $? != 0 ]]
	then
		echo "The parfile was not created successfully!"
	else
		echo "The parfile was created successfully!" | mailx -s "Database Backup was successfully executed!" stackcloud11@mkitconsulting.net
	fi

	#Tar File
	if [[ $status == "false" ]]
	then

		cd /backup/AWSSEP23/APEXDB
		tar -cvf ${schema_name}_${rnr}_${ts}.tar ${name}_${rnr}_${ts}.dmp ${name}_${rnr}_${ts}.log --remove-files

		#2 Day Policy Removal
		find /backup/AWSSEP23/APEXDB -name "*${rnr}*" -mtime +2 -exec rm {} \;

		#Printing results for dmp search
		ls -ltr /backup/AWSSEP23/APEXDB |grep ${rnr}_${ts}.dmp	
	fi
fi
}

#DatabaseMigration
DatabaseMig(){

#Database Backup Func
for name in $names
do
	Databkup $rnr $ts $name $status

	#SecureCopy Function
	if [[ /backup/AWSSEP23/APEXDB/${name}_${rnr}_${ts}.dmp ]];
	then
		"DB successful, starting secure copy."
		src=/backup/AWSSEP23/APEXDB/${name}_${rnr}_${ts}.dmp
		Secure_Copy $server $src $destserver $dest $user $status $key		
	else
		echo "DB failure."
		exit
	fi

	#Import Schema
	echo "userid ='/ as sysdba'">impdp_${name}_${rnr}.par
	echo "schemas =${name}">>impdp_${name}_${rnr}.par
	echo "dumpfile=${name}_${rnr}_${ts}.dmp">>impdp_${name}_${rnr}.par
	echo "logfile=${name}_${rnr}_${ts}.log">>impdp_${name}_${rnr}.par
	echo "directory=${bckupdir}">>impdp_${name}_${rnr}.par

	echo "export ORACLE_HOME="/u01/app/oracle/product/12.1.0/db_1"">impdp_"${rnr}".sh
	echo "export ORACLE_SID=HERC">>impdp_"${rnr}".sh
	echo "/u01/app/oracle/product/12.1.0/db_1/bin/impdp parfile=$dest/impdp_${name}_${destserver}.par">>impdp_"${rnr}".sh
	src=impdp_${name}_${reschem}.par
	Secure_Copy $server $dest $destserver $src $user $key	$status
	src=impdp_"${rnr}".sh
	dest=$destbase
	Secure_Copy $server $dest $destserver $src $user $key $status

	#Cleanup
	
	cd /backup/AWSSEP23/APEXDB
	tar -cvf ${name}_${reschem}_${ts}.tar /backup/AWSSEP23/APEXDB/${name}_${reschem}_${ts}.dmp /backup/AWSSEP23/APEXDB/${name}_${reschem}_${ts}.log --remove-files
	ls -ltr /backup/AWSSEP23/APEXDB |grep ${reschem}_${ts}.tar

	ssh -l $key $user@$destserver -T <<EOF
	cd $destbase
	ls -ltr
	cmod 744 impdp_"$rnr".sh
	. /home/oracle/scripts/practicedir_myl_sep23/impdp_"$rnr".sh

	cd $dest	
	tar -cvf ${schema}_${reschem}_${ts}.tar $dest/${name}_${reshem}_${ts}.dmp ${dest}/${name}_${reschem}_${ts}.log --remove-files
	ls -ltr |grep ${reschem}_${ts}.tar
EOF
	done
}


#main body
if [[ $# == 0 ]]; 
then
	read -p "What function are you trying to run?
backup
disk
data
securecopy
database-migration
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
			read -p "The database backup function requires 3 argument!
(Runner, Schema_Name(s), Directory)
Enter Arguments: " rnr sche bckupdir
			names=($sche)
			status="false"
			if [[$names > 1]] ; 
			then
				for name in $names
				do
					Databkup $rnr $name $bckupdir $ts $status
				done
			else
				name=$sche	
				Databkup $rnr $name $bckupdir $ts $status
			fi
		;;

		securecopy)
			read -p "The secure copy function requires 1 argument!
(ServerType: 'Onprem' or 'Cloud')
Enter Argument: " server
			if [[ $server == "Onprem" ]]; then
				read -p "Please enter source directory or file: " src
				read -p "Please enter the destination server: " destserver
				read -p "Please enter the destination directory path: " dest
				read -p "Please enter the username: " user
				Secure_Copy $server $src $destserver $dest $user
			elif [[ $server == "Cloud" ]]; then 
				read -p "Please enter the private key:" key
				read -p "Please enter source directory or file: " src
				read -p "Please enter the destination server: " destserver
				read -p "Please enter the destination directory path: " dest
				read -p "Please enter the username: " user
				Secure_Copy $server $src $destserver $dest $user $key
			fi
		;;

		database-migration)
			echo "The databsae migration function requires 2 arguments!"
			read -p "Please enter the Runner and ServerType(Onprem/Cloud): " rnr server
			read -p "Please enter schema(s) you'd like to backup: " names
			if [[ $server == "Onprem" ]]; then
				read -p "Please enter source directory or file: " src
				read -p "Please enter the destination server: " destserver
				read -p "Please enter the destination directory path: " dest
				read -p "Please enter the username: " user
			elif [[ $server == "Cloud" ]]; then
				read -p "Please enter the private key: " key
				read -p "Please enter source directory or file: " src
				read -p "Please enter the destination server: " destserver
				read -p "Please enter the destination directory path: " dest
				read -p "Please enter the username: " user
			else
				echo "Invalid Server Type"
				exit
			fi
			read -p "Please enter the remapped schema name: " reschem
			read -p "Please enter the name of the destination database: " destbase
			ts=`date '+%m%d%y%H%M%S'`
			status="true"
			databasemigration $rnr $server $names $src $destserver $dest $user $key $reschem $destbase $status
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
	status="false"
	if [[ $# != 4 ]]; then
		echo "Incorrect number of arguments given for database backup function!"
		read -p "The database backup function requires 3 argument!
(Runner, Directory)
Enter Arguments: " rnr bckupdir
		read -p "Now enter your schema(s) names!" name
		Databkup $rnr $name $bckupdir $ts $status
	else
		rnr=$2
		name=$3
		bckupdir=$4
		Databkup $rnr $name $bckupdir $ts $status
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
elif [[ $1 == "database-migration" ]]; then
	 if [[ $# != 2 ]]; then
		echo "The databsae migration function requires 2 arguments!"
		read -p "Please enter the Runner and ServerType(Onprem/Cloud): " rnr server read -p "Please enter the Runner and ServerType(Onprem/Cloud): " rnr server
		read -p "Please enter schema(s) you'd like to backup: " names
		if [[ $server == "Onprem" ]]; then
			read -p "Please enter source directory or file: " src
			read -p "Please enter the destination server: " destserver
			read -p "Please enter the destination directory path: " dest
			read -p "Please enter the username: " user
		elif [[ $server == "Cloud" ]]; then		
			read -p "Please enter the privat key: " key
			read -p "Please enter source directory or file: " src
			read -p "Please enter the destination server: " destserver
			read -p "Please enter the destination directory path: " dest
			read -p "Please enter the username: " user
			Secure_Copy $servertype $src $destserver $dest $user $key
		else
			echo "Please enter 'Onprem' or 'Cloud'"
			exit
		fi	
	elif [[ $# == 2 ]]; then
		read -p "Please enter schema(s) you'd like to backup: " names
		if [[ $server == "Onprem" ]]; then
			read -p "Please enter source directory or file: " src
			read -p "Please enter the destination server: " destserver
			read -p "Please enter the destination directory path: " dest
			read -p "Please enter the username: " user
		elif [[ $server == "Cloud" ]]; then
			read -p "Please enter the privat key: " key
			read -p "Please enter source directory or file: " src
			read -p "Please enter the destination server: " destserver
			read -p "Please enter the destination directory path: " dest
			read -p "Please enter the username: " user
		else
			echo "Please enter 'Onprem' or 'Cloud'"
			exit
		fi
		read -p "Please enter the remapped schema name: " reschem
		read -p "Please enter the name of the destination database: " destbase
		ts=`date '+%m%d%y%H%M%S'`		
		status="true"
		databasemigration $rnr $server $names $src $destserver $dest $user $key $reschem $destbase $status

	else
		echo "$function is not defined?
Please enter one of the following...
backup
disk
data
securecopy"
		exit
fi


