#!/user/bin/python

#Imports
import time, os

timestring=time.localtime()
TS=time.strftime("%d%m%y%H%M%S",timestring)
print(TS)
backup_base="/backp/AWSSEP23/APEXDB"
rnr="MYLES"
backup_dir=os.path.join(backup_base,rnr)

#Creating/Writing into file
try:
		file1=open("/home/oracle/scripts/practicedir_ynr_sep23/export_stack_temp_%s.par"%(TS),"w+")
		file1.write("userid='/ as sysdba'\nschemas=stack_temp\ndumpfile=stack_temp_%s.dmp\nlogfile=stack_temp_%s.log\ndirectory=DATA_PUMP_DIR"%(TS,TS))
		file1.close()
	
		file_read=open("/home/oracle/scripts/practicedir_myl_sep23/export_stack_temp_%s.par"%(TS),"r+")
		#print(file_read.read())
		file_read.close()

		file_name="export_stack_temp_%s.par"%(TS)
		file_path=os.path.join(os.getcwd(),"%s"%(file_name))
		print(file_path)
		
		export=open("/home/oracle/scripts/practicedir_myl_sep23/export.sh","w+")
		export.write(". /home/oracle/scripts/oracle_env_APEXDB.sh\nexpdp parfile=export_stack_temp_%s.par"%(TS))
		export.close()
		export_content="/home/oracle/scripts/practicedir_myl_sep23/export.sh"

		if os.path.isfile(file_path):
			print("Par File Exist")
		backup_path=os.path.join(backup_dir,TS)
		print(backup_path)
		
		os.popen("mkdir -p %s"%(backup_path))
		os.popen("chmod 700 %s"%(export_content))
		os.popen("%s"%(export_content))
except:
		print("Export Failed")

