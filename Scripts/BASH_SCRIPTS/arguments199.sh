#!/bin/bash







secure_copy()
{
if ( grep ${destination_sever} /home/oracle/scripts/practicedir_olu_sep23/onpremserver.txt )
then
	scp -r ${source_path} ${destination_server}:${destination_path}
elif ( grep ${destination_server} /home/oracle/scripts/practicedir_olu_sep23/cloudserver.txt )
then
	scp -r -i ${private_key} ${source_path} ${destination_server}:${destination_path}
else
	echo "server not found"
fi
}





#backup a file or directory from source to destination or check disk utilization

#function to backup file or directory
backup_f_d()
{
#create destination directory
mkdir -p ${destination}

#check exit status
if (( $? != 0 ))
then
   echo "failed to create destination directory"
else
	 echo  "copying ${source} to ${destination}"
fi

cp -r ${source} ${destination}

#check exit status
if (( $? != 0 ))
then
   echo "backup failed"
else
   echo "${source} copied successfully to ${destination}"
fi
}

#Database backup function
database_backup()
{

#Checking if database is running
if ( ps -ef |grep pmon | grep APEXDB )
then
   echo "database is running"
 
 #Setting Environment Variables
     . /home/oracle/scripts/oracle_env_APEXDB.sh

#check database status and confirm it is open
 sqlplus stack_temp/stackinc@APEXDB<<EOF
 set echo on feedback on
 spool /home/oracle/scripts/practicedir_olu_sep23/db_status.log
 show user
 select * from global_name;
 select status from v\$instance;
 spool off
EOF


if ( grep "OPEN" /home/oracle/scripts/practicedir_olu_sep23/db_status.log )
then
     echo "database is open"
else echo" database is not open"
fi



	db_schema="${schemaname}"
	for schema in $db_schema
	do	
   	#TS=`date '+%m%d%y%H%M%S'`
		echo "userid='/ as sysdba'" > expdp_${schema}_${runner}_${TS}.par
		echo "schemas=${schema}" >> expdp_${schema}_${runner}_${TS}.par
		echo "dumpfile=${schema}_${runner}_${TS}.dmp" >> expdp_${schema}_${runner}_${TS}.par
		echo "logfile=${schema}_${runner}_${TS}.log" >> expdp_${schema}_${runner}_${TS}.par
		echo "directory=$directory" >> expdp_${schema}_${runner}_${TS}.par


       
expdp parfile=expdp_${schema}_${runner}_${TS}.par

if ( grep "successfully completed" /backup/AWSSEP23/APEXDB/${schema}_${runner}_${TS}.log )
then
   echo "expdp backup successful"| mailx -s "Email Sent!" stackcloud11@mkitconsulting.net


#archive the log files
cd /backup/AWSSEP23/APEXDB

tar -cvf /backup/AWSSEP23/APEXDB/${schema}_${runner}_${TS}.tar *$runner* --remove-files

cd /home/oracle/scripts/practicedir_olu_sep23


#checking backup retention policy
find /backup/AWSSEP23/APEXDB/ -name "*runner*" -mtime +2 -exec rm -rf {} \;

else
   echo "expdp backup failed"
fi
done
else 
	echo "database is not open"


fi

}


data_migration()
{
database_backup $schemaname $runner $directory


#Making the import par.file

db_schema=${schemaname}
for schemas in $db_schema
do

	echo "userid='/as sysdba'" > impdp_${schemas}_${import_schema}_${TS}.par
	echo "schemas=$schemas" >> impdp_${schemas}_${import_schema}_${TS}.par
	echo "remap_schema=${schemas}:${import_schema}_migrated" >> impdp_${schemas}_${import_schema}_${TS}.par
	echo "dumpfile=${schemas}_${runner}_${TS}.dmp" >> impdp_${schemas}_${import_schema}_${TS}.par
	echo "logfile=impdp_${schemas}_${import_schema}.log" >> impdp_${schemas}_${import_schema}_${TS}.par
	echo "directory=$directory" >> impdp_${schemas}_${import_schema}_${TS}.par

#making the .sh file

	echo "export ORACLE_HOME=/u01/app/oracle/product/12.1.0/db_1" > import_${schemas}_${import_schema}_${TS}.sh
	echo "export ORACLE_SID=${db_name}" >> import_${schemas}_${import_schema}_${TS}.sh
	echo "/u01/app/oracle/product/12.1.0/db_1/bin/impdp parfile=${destination_path}impdp_${schemas}_${import_schema}_${TS}.par" >> import_${schemas}_${import_schema}_${TS}.sh


source_path="${sourcedb_path}${schemas}_${runner}_${TS}.tar import_${schemas}_${import_schema}_${TS}.sh impdp_${schemas}_${import_schema}_${TS}.par" 
secure_copy $private_key $source_path $destination_server $destination_path 



ssh -i $private_key $destination_sever "chmod 700 ${destination_path}import_${schemas}_${import_schema}_${TS}.sh"

ssh -i $private_key $destination_sever "mv ${destination_path}${schemas}_${runner}_${TS}.tar $destdb_path"

ssh -i $private_key $destination_sever "tar -xvf ${schemas}_${runner}_${TS}.tar -C $destdb_path" 

ssh -i $private_key $destination_sever "${destination_path}import_${schemas}_${import_schema}_${TS}.sh"

done
}
#function to check disk utilization
disk_utilization_check()
{


#extract utilization (number only) of specified disk
utilization=`df -h|grep ${disk}|awk '{print $4}'|sed 's/%//g'`

#compare disk utilization and specified threshold
if (( ${utilization} > ${threshold} ))
then
	echo "Disk utilization of ${disk} is over ${threshold}%"
else
	echo "Disk utilization of ${disk} is below ${threshold}%"
fi
}





#Main Body
TS=`date '+%m%d%y%H%M%S'`



#check for function in command line arguments or prompt user for function
if [[ $# == 0 ]] 
then 
	read -p "what function are you trying to run? disk_utilization_check database_backup secure_copy backup data_migration: " function 
	case $function in
		disk_utilization_check)
				read -p "Enter threshold: " threshold
	  			read -p "Enter disk: " disk
				#Call the disk utilization Function
		      disk_utilization_check $threshold $disk
	;;
	backup)
			read -p "Enter Source: " source
			read -p "Enter destination: " dest
			read -p "Enter runner: " runner
			destination=$dest/$TS/$runner
			#call the backup function
			backup_f_d $source $dest $runner
			#check database is running
	;;
	
	database_backup) 
				read -p "Enter DB schema: " schemaname
            read -p "Enter runner: " runner
				read -p "Enter directory: " directory
            #Call database_backup function
				database_backup $schemaname $runner $directory

	;;
	secure_copy)
				read -p "Do you want to push to? on-prem or cloud: " input						
				if [[ $input == "on-prem" ]] 
				then
				echo "enter argumnets for scp"
				read -p "Enter source dir or file path: " source_path
				read -p "Enter destination server: " destination_server
			   read -p "Enter destination path: " destination_path
			   #Call secure copy function for on-prem
				secure_copy $source_path $destination_server $destination_path
				elif [[ $input == "cloud" ]]
	         then
   			echo "Enter arguments for scp"
   			read -p "Enter private key path: " private_key
   			read -p "Enter source dir or file path: " source_path
 			   read -p "Enter destination server: " destination_server
   			read -p "Enter destination path: " destination_path
				#Call secure copy function for cloud
				secure_copy $private_key $source_path $destination_server $destination_path
				fi
				;;
	 data_migration)
           	read -p "Please enter the runner and scheme name: " runner schemaname
           	read -p "Please enter the directory: " directory
				read -p "Please enter the privatekey: " private_key
				read -p "Please enter the  destination server: " destination_server
				read -p "Please enter the  destination path: " destination_path 
				read -p "Please entre the schemaname to import: " import_schema
				read -p "Please enter the  physical db destination path for dump file: " destdb_path
          	read -p "Please enter target server db name: " db_name
				#Call data migration function
            data_migration $schemaname $runner $directory $private_key $destination_server $destination_path $import_schema $destdb_path $db_name
	;;
	
	*)
				echo "undefined function"
;;	
esac




				#When Command Line Arguments are entered
				elif [[ $1 == "backup" && $# == 4 ]]
				then
				source=$2
				#destination provided by runner
				dest=$3
				runner=$4
				#path to backup destination
				destination=$dest/$TS/$runner
				#call backup function
				backup_f_d $source $dest $runner

				elif [[ $1 == "backup" && $# != 4 ]]
				then
				echo "USAGE:Provide the 4 command line arguments and function to run this script"
				echo "Example:$0 backup /source /dest runner"

				elif [[ $1 == "disk_utilization_check" && $# == 3 ]]
				then
				echo "USAGE:provide 3 command line arguments and function to run this script"
				echo "Example:$0 disk_utlization_check 70% /u01"
   			disk_utlization_check
				threshold=$2
				disk=$3
				#call the disk utilization Function
				disk_utilization_check $threshold $disk

				#Checking the SCP function
				elif [[ $1 == "secure_copy" && $# == 4 ]]
				then 
				source_path=$2
				destination_server=$3
	   		destination_path=$4
				#Call secure copy function for on-prem
				secure_copy $source_path $destination_server $destination_path
				elif [[ $1 == "secure_copy" && $# == 5 ]]
				then
				private_key=$2
				source_path=$3
      		destination_server=$4
				destination_path=$5
				#call secure copy function for cloud
				secure_copy $private_key $source_path $destination_server $destination_path
				else 
				echo " function or incorrect argument undefined "
fi

#!/bin/bash







secure_copy()
{
if ( grep ${destination_sever} /home/oracle/scripts/practicedir_olu_sep23/onpremserver.txt )
then
	scp -r ${source_path} ${destination_server}:${destination_path}
elif ( grep ${destination_server} /home/oracle/scripts/practicedir_olu_sep23/cloudserver.txt )
then
	scp -r -i ${private_key} ${source_path} ${destination_server}:${destination_path}
else
	echo "server not found"
fi
}





#backup a file or directory from source to destination or check disk utilization

#function to backup file or directory
backup_f_d()
{
#create destination directory
mkdir -p ${destination}

#check exit status
if (( $? != 0 ))
then
   echo "failed to create destination directory"
else
	 echo  "copying ${source} to ${destination}"
fi

cp -r ${source} ${destination}

#check exit status
if (( $? != 0 ))
then
   echo "backup failed"
else
   echo "${source} copied successfully to ${destination}"
fi
}

#Database backup function
database_backup()
{

#Checking if database is running
if ( ps -ef |grep pmon | grep APEXDB )
then
   echo "database is running"
 
 #Setting Environment Variables
     . /home/oracle/scripts/oracle_env_APEXDB.sh

#check database status and confirm it is open
 sqlplus stack_temp/stackinc@APEXDB<<EOF
 set echo on feedback on
 spool /home/oracle/scripts/practicedir_olu_sep23/db_status.log
 show user
 select * from global_name;
 select status from v\$instance;
 spool off
EOF


if ( grep "OPEN" /home/oracle/scripts/practicedir_olu_sep23/db_status.log )
then
     echo "database is open"
else echo" database is not open"
fi



	db_schema="${schemaname}"
	for schema in $db_schema
	do	
   	#TS=`date '+%m%d%y%H%M%S'`
		echo "userid='/ as sysdba'" > expdp_${schema}_${runner}_${TS}.par
		echo "schemas=${schema}" >> expdp_${schema}_${runner}_${TS}.par
		echo "dumpfile=${schema}_${runner}_${TS}.dmp" >> expdp_${schema}_${runner}_${TS}.par
		echo "logfile=${schema}_${runner}_${TS}.log" >> expdp_${schema}_${runner}_${TS}.par
		echo "directory=$directory" >> expdp_${schema}_${runner}_${TS}.par


       
expdp parfile=expdp_${schema}_${runner}_${TS}.par

if ( grep "successfully completed" /backup/AWSSEP23/APEXDB/${schema}_${runner}_${TS}.log )
then
   echo "expdp backup successful"| mailx -s "Email Sent!" stackcloud11@mkitconsulting.net


#archive the log files
cd /backup/AWSSEP23/APEXDB

tar -cvf /backup/AWSSEP23/APEXDB/${schema}_${runner}_${TS}.tar *$runner* --remove-files

cd /home/oracle/scripts/practicedir_olu_sep23


#checking backup retention policy
find /backup/AWSSEP23/APEXDB/ -name "*runner*" -mtime +2 -exec rm -rf {} \;

else
   echo "expdp backup failed"
fi
done
else 
	echo "database is not open"


fi

}


data_migration()
{
database_backup $schemaname $runner $directory


#Making the import par.file

db_schema=${schemaname}
for schemas in $db_schema
do

	echo "userid='/as sysdba'" > impdp_${schemas}_${import_schema}_${TS}.par
	echo "schemas=$schemas" >> impdp_${schemas}_${import_schema}_${TS}.par
	echo "remap_schema=${schemas}:${import_schema}_migrated" >> impdp_${schemas}_${import_schema}_${TS}.par
	echo "dumpfile=${schemas}_${runner}_${TS}.dmp" >> impdp_${schemas}_${import_schema}_${TS}.par
	echo "logfile=impdp_${schemas}_${import_schema}.log" >> impdp_${schemas}_${import_schema}_${TS}.par
	echo "directory=$directory" >> impdp_${schemas}_${import_schema}_${TS}.par

#making the .sh file

	echo "export ORACLE_HOME=/u01/app/oracle/product/12.1.0/db_1" > import_${schemas}_${import_schema}_${TS}.sh
	echo "export ORACLE_SID=${db_name}" >> import_${schemas}_${import_schema}_${TS}.sh
	echo "/u01/app/oracle/product/12.1.0/db_1/bin/impdp parfile=${destination_path}impdp_${schemas}_${import_schema}_${TS}.par" >> import_${schemas}_${import_schema}_${TS}.sh


source_path="${sourcedb_path}${schemas}_${runner}_${TS}.tar import_${schemas}_${import_schema}_${TS}.sh impdp_${schemas}_${import_schema}_${TS}.par" 
secure_copy $private_key $source_path $destination_server $destination_path 



ssh -i $private_key $destination_sever "chmod 700 ${destination_path}import_${schemas}_${import_schema}_${TS}.sh"

ssh -i $private_key $destination_sever "mv ${destination_path}${schemas}_${runner}_${TS}.tar $destdb_path"

ssh -i $private_key $destination_sever "tar -xvf ${schemas}_${runner}_${TS}.tar -C $destdb_path" 

ssh -i $private_key $destination_sever "${destination_path}import_${schemas}_${import_schema}_${TS}.sh"

done
}
#function to check disk utilization
disk_utilization_check()
{


#extract utilization (number only) of specified disk
utilization=`df -h|grep ${disk}|awk '{print $4}'|sed 's/%//g'`

#compare disk utilization and specified threshold
if (( ${utilization} > ${threshold} ))
then
	echo "Disk utilization of ${disk} is over ${threshold}%"
else
	echo "Disk utilization of ${disk} is below ${threshold}%"
fi
}





#Main Body
TS=`date '+%m%d%y%H%M%S'`



#check for function in command line arguments or prompt user for function
if [[ $# == 0 ]] 
then 
	read -p "what function are you trying to run? disk_utilization_check database_backup secure_copy backup data_migration: " function 
	case $function in
		disk_utilization_check)
				read -p "Enter threshold: " threshold
	  			read -p "Enter disk: " disk
				#Call the disk utilization Function
		      disk_utilization_check $threshold $disk
	;;
	backup)
			read -p "Enter Source: " source
			read -p "Enter destination: " dest
			read -p "Enter runner: " runner
			destination=$dest/$TS/$runner
			#call the backup function
			backup_f_d $source $dest $runner
			#check database is running
	;;
	
	database_backup) 
				read -p "Enter DB schema: " schemaname
            read -p "Enter runner: " runner
				read -p "Enter directory: " directory
            #Call database_backup function
				database_backup $schemaname $runner $directory

	;;
	secure_copy)
				read -p "Do you want to push to? on-prem or cloud: " input						
				if [[ $input == "on-prem" ]] 
				then
				echo "enter argumnets for scp"
				read -p "Enter source dir or file path: " source_path
				read -p "Enter destination server: " destination_server
			   read -p "Enter destination path: " destination_path
			   #Call secure copy function for on-prem
				secure_copy $source_path $destination_server $destination_path
				elif [[ $input == "cloud" ]]
	         then
   			echo "Enter arguments for scp"
   			read -p "Enter private key path: " private_key
   			read -p "Enter source dir or file path: " source_path
 			   read -p "Enter destination server: " destination_server
   			read -p "Enter destination path: " destination_path
				#Call secure copy function for cloud
				secure_copy $private_key $source_path $destination_server $destination_path
				fi
				;;
	 data_migration)
           	read -p "Enter DB schema: " schemaname
           	read -p "Enter runner: " runner
           	read -p "Enter directory: " directory
				read -p "Enter privatekey: " private_key
				read -p "Enter destination server: " destination_server
				read -p "Enter destination path: " destination_path 
				read -p "Enter schemaname to import: " import_schema
				read -p "Enter physical db destination path for .dmp file: " destdb_path
          	read -p "Enter target server db name: " db_name
				#Call data migration function
            data_migration $schemaname $runner $directory $private_key $destination_server $destination_path $import_schema $destdb_path $db_name
	;;
	
	*)
				echo "undefined function"
;;	
esac




				#When Command Line Arguments are entered
				elif [[ $1 == "backup" && $# == 4 ]]
				then
				source=$2
				#destination provided by runner
				dest=$3
				runner=$4
				#path to backup destination
				destination=$dest/$TS/$runner
				#call backup function
				backup_f_d $source $dest $runner

				elif [[ $1 == "backup" && $# != 4 ]]
				then
				echo "USAGE:Provide the 4 command line arguments and function to run this script"
				echo "Example:$0 backup /source /dest runner"

				elif [[ $1 == "disk_utilization_check" && $# == 3 ]]
				then
				echo "USAGE:provide 3 command line arguments and function to run this script"
				echo "Example:$0 disk_utlization_check 70% /u01"
   			disk_utlization_check
				threshold=$2
				disk=$3
				#call the disk utilization Function
				disk_utilization_check $threshold $disk

				#Checking the SCP function
				elif [[ $1 == "secure_copy" && $# == 4 ]]
				then 
				source_path=$2
				destination_server=$3
	   		destination_path=$4
				#Call secure copy function for on-prem
				secure_copy $source_path $destination_server $destination_path
				elif [[ $1 == "secure_copy" && $# == 5 ]]
				then
				private_key=$2
				source_path=$3
      		destination_server=$4
				destination_path=$5
				#call secure copy function for cloud
				secure_copy $private_key $source_path $destination_server $destination_path
				else 
				echo " function or incorrect argument undefined "
fi

