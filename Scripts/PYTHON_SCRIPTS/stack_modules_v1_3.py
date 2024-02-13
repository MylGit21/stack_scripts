#!/usr/bin/python


# Modules
import boto3
import gzip
import os
import psutil
import smtplib
import subprocess
import tarfile
import time
import shutil as s
import cx_Oracle as cx
from pathlib import Path
from botocore.exceptions import ClientError

# Variables
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
global LastStartTime


# Sub Functions
def print_colored_text(**kwargs):
    print("{}{}\033[0m".format(kwargs["color_code"], kwargs["text"]))


def STACK_EMAIL(**kwargs):
    kwargs["FROM"] = "oracle@MKIT-DEV-OEM.localdomain"
    kwargs["MSG"] = ("\n".join(
        ("From: {}".format(kwargs["FROM"]), "To: {}".format(kwargs["TO_EMAIL"]),
         "Subject: {}\n".format(kwargs["SUBJECT"]),
         "{}".format(kwargs["BODY"]))))
    with smtplib.SMTP('localhost') as my_server:
        my_server.sendmail(kwargs["FROM"], kwargs["TO_EMAIL"], kwargs["MSG"])
        print_colored_text(text="Email sent successfully to %s" % kwargs["TO_EMAIL"], color_code=kwargs["COLOR"])


def Gzip(**kwargs):
    print_colored_text(text="Zipping {} to {}!".format(kwargs["Src"], kwargs["Dst"]), color_code=YELLOW)

    try:
        # if path is a file normally gzip
        if os.path.isfile(kwargs["Src"]):
            print("Source is a file!")
            with open(kwargs["Src"], 'rb') as Ginput:
                with gzip.open("{}.gz".format(kwargs["Src"]), 'wb') as Goutput:
                    Goutput.writelines(Ginput)
                    print_colored_text(text="Zipping {} to {} was successful!".format(kwargs["Src"], kwargs["Dst"]),
                                       color_code=GREEN)
        # if path is a directory, use tar.gz
        elif os.path.isdir(kwargs["Src"]):
            print("Source is a directory!")
            with tarfile.open("{}.tar.gz".format(kwargs["Src"]), "w:gz") as tar:
                tar.add(kwargs["Src"])
                print_colored_text(text="Tar Zipping {} to {} was successful!".format(kwargs["Src"], kwargs["Dst"]),
                                   color_code=GREEN)
        else:
            print_colored_text(text="File is neither a file or directory!", color_code=RED)
    except:
        print_colored_text(text="FAILED TO GZIP {}".format(kwargs["Src"]), color_code=RED)
        raise ValueError("Gzip Failed")


def list_files_in_directory(**kwargs):
    path = Path(kwargs["directory"])
    print_colored_text(text="\n{} contents: ".format(kwargs["directory"]), color_code=YELLOW)
    for file in path.iterdir():
        print(file.name)


def DB_Connection(**kwargs):
    # print(kwargs)
    connection = cx.connect(user="STACK_MYL_SEP23", password="stackinc", dsn="MKIT-DEV-OEM/APEXDB")
    print_colored_text(text="Connection Version: {}".format(connection.version), color_code=YELLOW)

    cursor = connection.cursor()
    email = cursor.execute("SELECT MONITORING_EMAIL FROM PROD_OPERATIONS WHERE OP_ID = '{}'".format(kwargs["OP_ID"])).fetchall()[0][0]

    # If starttime but no endtime given do initial set up
    if "OP_STARTTIME" in kwargs and "OP_ENDTIME" not in kwargs:
        print_colored_text(text="FUNCTION LOGGED!", color_code=GREEN)
        cursor.execute("""INSERT INTO PROD_ACTIVITIES VALUES (:OP_ID_INS, :OP_STARTTIME_INS, :OP_ENDTIME_INS, :RUNNER_INS, :STATUS_INS, :MON_EMAIL_INS)""",
                            OP_ID_INS=kwargs["OP_ID"],
                            OP_STARTTIME_INS=kwargs["OP_STARTTIME"],
                            OP_ENDTIME_INS=kwargs["OP_STARTTIME"],
                            RUNNER_INS=kwargs["RUNNER"],
                            STATUS_INS=kwargs["STATUS"],
                            MON_EMAIL_INS=email)
    # If endtime but not starttime given update the initial set up
    elif 'OP_ENDTIME' in kwargs and 'OP_STARTTIME' not in kwargs:
        print_colored_text(text="LOG UPDATED!", color_code=GREEN)
        cursor.execute("update PROD_ACTIVITIES set OP_ENDTIME = :OP_ENDTIME_INS, STATUS = :STATUS_INS where STATUS = 'RUNNING' and RUNNER = :RUNNER_INS and OP_ID = :OP_ID_INS""",
                       OP_ENDTIME_INS=kwargs["OP_ENDTIME"],
                       STATUS_INS=kwargs["STATUS"],
                       RUNNER_INS=kwargs["RUNNER"],
                       OP_ID_INS=kwargs["OP_ID"])
    # If both endtime and starttime set for manual logging
    elif 'OP_ENDTIME' in kwargs and 'OP_STARTTIME' in kwargs:
        print_colored_text(text="FUNCTION LOGGED!", color_code=GREEN)
        cursor.execute(
            """INSERT INTO PROD_ACTIVITIES VALUES (:OP_ID_INS, :OP_STARTTIME_INS, :OP_ENDTIME_INS, :RUNNER_INS, :STATUS_INS, :MON_EMAIL_INS)""",
            OP_ID_INS=kwargs["OP_ID"],
            OP_STARTTIME_INS=kwargs["OP_STARTTIME"],
            OP_ENDTIME_INS=kwargs["OP_ENDTIME"],
            RUNNER_INS=kwargs["RUNNER"],
            STATUS_INS=kwargs["STATUS"],
            MON_EMAIL_INS=email)
    connection.commit()


# Primary Functions
def Backup(**kwargs):
    DB_Connection(OP_ID=4, OP_NAME="File/Directory_Copy", OP_TYPE="Backup", OP_STARTTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="RUNNING")
    print_colored_text(text="Backing up %s to %s" % (kwargs["Source"], kwargs["Destination"]), color_code=YELLOW)
    try:
        # check for timestamp
        TS = input("\nAdd a timestamp? (Leave blank for no): ")
        if TS != "":
            TS = time.strftime("%d%m%Y%H%M", time.localtime())

        # if src is a directory then copytree
        if os.path.isdir(kwargs["Source"]):
            s.copytree(kwargs["Source"], os.path.join(kwargs["Destination"], kwargs["Source"] + TS))
            print_colored_text(
                text="Successfully copied {} to {}!".format(kwargs["Source"] + TS, kwargs["Destination"]),
                color_code=GREEN)
        else:
            s.copy(kwargs["Source"], os.path.join(kwargs["Destination"], kwargs["Source"] + TS))
            print_colored_text(
                text="Successfully copied {} to {}!".format(kwargs["Source"] + TS, kwargs["Destination"]),
                color_code=GREEN)

        # check for zip
        ZG = input("\nZip this file/directory? (Leave blank for no): ")
        if ZG != "":
            # gzip the file
            Gzip(Src=os.path.join(kwargs["Destination"], kwargs["Source"] + TS), Dst=kwargs["Destination"])

            if os.path.isfile(kwargs["Source"]):
                os.remove(os.path.join(kwargs["Destination"], kwargs["Source"] + TS))
            elif os.path.isdir(kwargs["Source"]):
                s.rmtree(os.path.join(kwargs["Destination"], kwargs["Source"] + TS))

        # list new files in directory
        list_files_in_directory(directory=kwargs["Destination"])
        DB_Connection(OP_ID=4, OP_NAME="File/Directory_Copy", OP_TYPE="Backup", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="COMPLETED")
    except:
        print_colored_text(text="Failed to backup %s to %s" % (kwargs["Source"], kwargs["Destination"]), color_code=RED)
        DB_Connection(OP_ID=4, OP_NAME="File/Directory_Copy", OP_TYPE="Backup", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="ERROR")
        raise ValueError("Backup Failed")


def aws_create_user(**kwargs):
    try:
        iam = boto3.client(service_name=kwargs["Service"])
        re = iam.create_user(UserName=kwargs["User"])
        print_colored_text(text="Success!", color_code=GREEN)
        return kwargs["User"]  # Return the created user name
    except ClientError as error:
        print_colored_text(text=error.response, color_code=RED)
        if error.response["Error"]["Code"] == "EntityAlreadyExists":
            print("User already exists.. Use the same user?")
            val = input("Enter (y or n): ")
            if val == 'y':
                print("You want to use the same user")
                return kwargs["User"]
            else:
                print("You want to create a new user")
                new_user = input("Enter username: ")
                response = iam.create_user(UserName=new_user)
                print_colored_text(text="Success!", color_code=GREEN)
                return new_user
        else:
            raise ValueError("Unexpected error occurred while creating user")


def aws_create_group(**kwargs):
    admin_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
    try:
        iam = boto3.client(service_name=kwargs["Service"])
        group_name = kwargs["Group"]

        # Check if the group already exists
        iam.get_group(GroupName=group_name)

        print_colored_text(text="Group '{}' already exists.".format(group_name), color_code=RED)
        print("Do you want to use the same group?")
        val = input("Enter (y or n): ")
        if val.lower() == 'y':
            print("You want to use the same group")
            pass
        else:
            print("You want to create a new group")
            new_group = input("Enter group name: ")
            response = iam.create_group(GroupName=new_group)
            print(response)
            print_colored_text(text="Success!", color_code=GREEN)

        # Attach the admin policy to the group
        iam.attach_group_policy(GroupName=group_name, PolicyArn=admin_policy_arn)
        print_colored_text(text="Admin policy attached to the group '{}'.".format(group_name), color_code=YELLOW)

    except ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchEntity":
            # Group doesn't exist, create it
            response = iam.create_group(GroupName=group_name)
            print(response)
            print_colored_text(text="Success!", color_code=GREEN)

            # Attach the admin policy to the newly created group
            iam.attach_group_policy(GroupName=group_name, PolicyArn=admin_policy_arn)
            print_colored_text(text="Admin policy attached to the group '{}'.".format(group_name), color_code=YELLOW)

        else:
            print_colored_text(text=error.response, color_code=RED)
            raise ValueError("Unexpected error occurred while creating group")


def aws_attach_user_group(**kwargs):
    try:
        iam = boto3.client(service_name=kwargs["Service"])
        user_name = aws_create_user(Service=kwargs["Service"], User=kwargs["User"])
        group_name = kwargs["Group"]

        # Attach the user to the group
        iam.add_user_to_group(GroupName=group_name, UserName=user_name)
        print_colored_text(text="User '{}' attached to group '{}'.".format(user_name,group_name), color_code=GREEN)

        # Set up login profile for the user
        pswrd = input("Enter password for user '{}': ".format(user_name))
        iam.create_login_profile(UserName=user_name, Password=pswrd)
        print_colored_text(text="Login profile created for user '{}'.".format(user_name), color_code=GREEN)

    except ClientError as error:
        print_colored_text(text="Error: {}".format(error.response['Error']['Message']), color_code=RED)


def UnGzip(**kwargs):
    print_colored_text(text="Unzipping {}!".format(kwargs["Absolute_Path"]), color_code=YELLOW)
    try:
        tar = tarfile.open(kwargs["Absolute_Path"])
        tar.extractall()
        tar.close
    except:
        print("Could not unzip file")

    dmpfiletest = os.path.splitext(kwargs["Absolute_Path"])[0]
    dmpfile = (os.path.basename(kwargs["Absolute_Path"]))
    print(dmpfile)
    return dmpfile


def Disk_Maintenance_Check_On_Prem(**kwargs):
    DB_Connection(OP_ID=5, OP_NAME="Disk_Monitoring", OP_TYPE="Monitoring", OP_STARTTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="RUNNING")
    try:
        # get disk usage using psutil
        disk_usage = psutil.disk_usage(kwargs["Disk"])

        # extract the usage percentage
        usage_percent = disk_usage.percent

        # Check if the disk utilization exceeds the threshold
        if int(usage_percent) > int(kwargs["Threshold"]):
            print("Disk utilization threshold breached for {}. Current utilization: {}".format(kwargs["Disk"],
                                                                                               usage_percent))
        else:
            print(
                "Disk utilization within threshold for {}. Current utilization: {}".format(kwargs["Disk"],
                                                                                           usage_percent))
        DB_Connection(OP_ID=5, OP_NAME="Disk_Monitoring", OP_TYPE="Monitoring", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'),
                      RUNNER="MYLES", STATUS="COMPLETED")
    except Exception as e:
        print("Failed to check disk usage", e)
        DB_Connection(OP_ID=5, OP_NAME="Disk_Monitoring", OP_TYPE="Monitoring",OP_STARTTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES",STATUS="ERROR")
        raise ValueError("Disk Check Failed")


def SmartDiskMonitor(**kwargs):
    while True:
        disk_usage = psutil.disk_usage(kwargs["Disk"])
        usage_percent = disk_usage.percent
        print("Disk utilization is {}".format(usage_percent))

        # Break Loop Manually
        if os.path.isfile("/home/oracle/scripts/practicedir_myl_sep23/Python/logstop.txt"):
            print_colored_text(text="{} is back under threshold!".format(kwargs["Disk"]), color_code=GREEN)
            break
        time.sleep(5)

        # Alert if over 90%
        if int(usage_percent) > 90:
            print_colored_text(text="[WARNING] DISK USAGE IS OVER 90% THRESHOLD!\nChecking again in 1 minute.", color_code=RED)
            STACK_EMAIL(TO_EMAIL="stackcloud11@mkitconsulting.net",SUBJECT="Disk Utilization Alert, Breached 90%",FROM="oracle@MKIT-DEV-OEM.localdomain",BODY="Disk {} usage is over 90%. Checking again in 1 minute.".format(kwargs["Disk"]), COLOR=YELLOW)
            time.sleep(60)
        # Alert if over 80%
        elif int(usage_percent) > 80:
            print_colored_text(text="[WARNING] DISK USAGE IS OVER 80% THRESHOLD\nChecking again in 5 minutes.", color_code=RED)
            STACK_EMAIL(TO_EMAIL="stackcloud11@mkitconsulting.net", SUBJECT="Disk Utilization Alert, Breached 90%", FROM="oracle@MKIT-DEV-OEM.localdomain", BODY="Disk {} usage is over 80%. Checking again in 5 minutes.".format(kwargs["Disk"]), COLOR=YELLOW)
            time.sleep(10)

def DatabaseBackup(**kwargs):
    TS = time.strftime("%d%m%Y%H%M%S", time.localtime())
    backup_base = "/backup/AWSSEP23/APEXDB/SAMD"
    backup_dir = os.path.join(backup_base, kwargs["Associated_Runner"])
    DB_Connection(OP_ID=1, OP_NAME="Export", OP_TYPE="Backup", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="RUNNING")
    try:
        file = open("/home/oracle/scripts/practicedir_myl_sep23/export_stack_temp{}_{}.par".format('MYLES',TS), "w+")
        file.write(
            "userid='/ as sysdba'\nschemas={}\ndumpfile=stack_temp_{}.dmp\nlogfile=stack_temp_{}.log\ndirectory=DATA_PUMP_DIR".format(
                kwargs["Schema_Name"], TS, TS))
        file.close()

        file_read = open("/home/oracle/scripts/practicedir_myl_sep23/export_stack_temp{}_{}.par".format('MYLES',TS), "r+")
        file_content = file_read.read()

        print(file_content)
        file_read.close()
        file_name = "export_stack_temp_{}_{}.par".format('MYLES',TS)
        file_path = os.path.join("/home/oracle/scripts/practicedir_myl_sep23", "{}".format(file_name))
        print_colored_text(text=file_path, color_code=RED)

        export = open("/home/oracle/scripts/practicedir_myl_sep23/export.sh", "w+")
        export.write(". /home/oracle/scripts/oracle_env_APEXDB.sh\nexpdp parfile={}".format(file_path))
        export.close()
        export_content = "/home/oracle/scripts/practicedir_myl_sep23/export.sh"

        if os.path.isfile(file_path):
            print("Par file exist!")
        backup_path = os.path.join(backup_dir, TS)
        print(backup_path)

        os.popen("mkdir -p %s" % backup_path)
        os.popen("chmod 700 %s" % export_content)
        os.popen("%s" % export_content)
        DB_Connection(OP_ID=1, OP_NAME="Export", OP_TYPE="Backup", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="COMPLETED")
    except:
        print("Export Failed")
        DB_Connection(OP_ID=1, OP_NAME="Export", OP_TYPE="Backup", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="ERROR")
        raise ValueError("DataBase Backup Failed")


def DatabaseImport(**kwargs):
    TS = time.strftime("%d%m%Y%H%M%S", time.localtime())
    DB_Connection(OP_ID=2, OP_NAME="Import", OP_TYPE="Backup", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="RUNNING")

    try:
        strippedpatha = os.path.split(os.path.splitext(kwargs["tarfile"])[0])[0]
        strippedpath = os.path.basename(strippedpatha)

        if os.path.exists("{}/{}".format(kwargs["BackupLocation"], strippedpath)):
            print("File Exist")
        else:
            src = "{}/{}".format(kwargs["BackupLocation"], strippedpath)
            dst = "/backup/AWSSEP23/{}".format(kwargs["DatabaseName"])
            Backup(Source=src, Destination=dst)

            imp = "userid='/ as sysdba'\nschemas={}\nremap_schema={}:{}_{}\ndumpfile={}\nlogfile={}_{}_{}.log\ndirectory={}\ntable_exist_action=replace".format(kwargs["Schema_Name"], kwargs["Schema_Name"], kwargs["Schema_Name"], kwargs["Runner"], strippedpath, kwargs["Schema_Name"], kwargs["Runner"], TS, kwargs["Directory"])
            backup_path = os.path.join(kwargs["BackupLocation"], kwargs["Runner"])
            file_path = os.path.join(backup_path, TS)

            imp_write = ". /home/oracle/scripts/oracle_env_{}.sh\n248 impdp parfile={}/impdp_{}_{}_{}.par".format(kwargs["DatabaseName"], kwargs["ConfigPath"], kwargs["Schema_Name"], kwargs["Runner"], TS)
            import_sh = "{}/impdp_{}_{}_{}.sh".format(kwargs["ConfigPath"], kwargs["Schema_Name"], kwargs["Runner"], TS)

            file = open("{}/impdp_{}_{}_{}.par".format(kwargs["ConfigPath"], kwargs["Schema_Name"], kwargs["Runner"], TS), "w+")
            file.write("{}".format(imp))
            file.close()

            file = open("{}/impdp_{}_{}_{}.par".format(kwargs["ConfigPath"], kwargs["Schema_Name"], kwargs["Runner"], TS), "r+")
            file_content = file.read()
            print(file_content)
            file.close()

            file = open("{}/impdp_{}_{}_{}.sh".format(kwargs["ConfigPath"], kwargs["Schema_Name"], kwargs["Runner"], TS), "w+")
            file.write("{}".format(imp_write))
            file.close()

            file = open("{}/impdp_{}_{}_{}.sh".format(kwargs["ConfigPath"], kwargs["Schema_Name"], kwargs["Runner"], TS), "r+")
            file_content = file.read()
            print(file_content)
            file.close()

            os.popen("mkdir -p {}".format(file_path))
            os.popen("chmod 700 {}".format(import_sh))
            subprocess.call(['sh', "{}".format(import_sh)])

        DB_Connection(OP_ID=2, OP_NAME="Import", OP_TYPE="Backup", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="COMPLETED")
    except Exception as e:
        DB_Connection(OP_ID=2, OP_NAME="Import", OP_TYPE="Backup", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="ERROR")
        print(e)


def Database_Migration(**kwargs):
    TS = time.strftime("%d%m%Y%H%M%S", time.localtime())
    DB_Connection(OP_ID=3, OP_NAME="Data_Migration", OP_TYPE="Migration", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="RUNNING")
    # Setting Variables
    filefig = "userid='/ as sysdba'\nschemas=%s\nremap_schema={}:{}_{}_MIGRATED\ndumpfile={}_{}_{}.dmp\nlogfile=impdp_{}_{}.log\ntable_exist_action=replace".format(
        kwargs["Schema_Name"], kwargs["Schema_Name"], kwargs["Schema_Name"], kwargs["Associated_Runner"],
        kwargs["Schema_Name"],
        kwargs["Associated_Runner"], TS, kwargs["Schema_Name"], kwargs["Destination_Schema"], kwargs["Directory"])
    local_dir = "/home/oracle/scripts/practicedir_myl_sep23"
    config_file_path = "{}/impdp_{}_{}_{}.par".format(local_dir, kwargs["Schema_Name"], kwargs["Destination_Schema"],
                                                      TS)
    dumpfile_path = "{}/{}_{}_{}.dmp".format(kwargs["Backup_Directory"], kwargs["Schema_Name"],
                                             kwargs["Associated_Runner"],
                                             TS)
    dest_dump_path = "/backup/AWSSEP23/{}".format(kwargs["Destination_Database"])
    kwargs["Absolute_Dumpfile_Path"] = dumpfile_path
    try:
        DatabaseBackup(**kwargs)

        Absolute_Path = "{}/{}_{}_{}.dmp.gz".format(kwargs["Backup_Directory"], kwargs["Schema_Name"],
                                                    kwargs["Associated_Runner"], TS)
        print("Absolute path before unzipping:", Absolute_Path)

        UnGzip(Absolute_Path)

        # Writing the config par file
        par = open(config_file_path, "w+")
        print("File name is:", par.name)
        par.write("{}".format(filefig))
        par.close()

        par = open(config_file_path, "r+")
        file_content = par.read()
        par.close()

        impor = open("{}/import.sh".format(local_dir), "w+")
        impor.write(". /home/oracle/scripts/oracle_env_{}.sh\nimpdp parfile={}".format(kwargs["Destination_Database"],
                                                                                       config_file_path))
        impor.close()
        impor_content = "{}/import.sh".format(local_dir)
        print(impor_content)

        # Copying unzipped dump file
        s.copy(dumpfile_path, dest_dump_path)

        os.popen("chmod 700 {}".format(impor_content))
        os.popen("{}".format(impor_content))
        DB_Connection(OP_ID=3, OP_NAME="Data_Migration", OP_TYPE="Migration", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="COMPLETED")
    except Exception as e:
        DB_Connection(OP_ID=3, OP_NAME="Data_Migration", OP_TYPE="Migration", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="ERROR")
        print(e)


# Function Dictionary
functions = {
    "Backup": {
        "function": Backup,
        "args": ["Source", "Destination"]
    },
    "DatabaseBackup": {
        "function": DatabaseBackup,
        "args": ["Associated_Runner", "Schema_Name"]
    },
    "DB_Connection": {
        "function": DB_Connection,
        "args": ["OP_ID", "OP_NAME", "OP_TYPE", "OP_STARTTIME", "RUNNER", "STATUS", "MON_EMAIL", "OP_ENDTIME"]
    },
    "DiskCheck": {
        "function": Disk_Maintenance_Check_On_Prem,
        "args": ["Disk", "Threshold"]
    },
    "SmartDiskMonitor": {
        "function": SmartDiskMonitor,
        "args": ["Disk"]
    },
    "UnGzip": {
        "function": UnGzip,
        "args": ["Absolute_Path"]
    },
    "DatabaseImport": {
        "function": DatabaseImport,
        "args": ["tarfile", "Schema_Name", "BackupLocation", "DatabaseName", "Runner", "ConfigPath", "Directory"]
    },
    "StackEmail": {
        "function": STACK_EMAIL,
        "args": ["SUBJECT", "BODY", "TO_EMAIL"]
    },
    "aws_create_user": {
        "function": aws_create_user,
        "args": ["Service", "User"]
    },
    "aws_create_group": {
        "function": aws_create_group,
        "args": ["Service", "Group"]
    },
    "aws_attach_user_group": {
        "function": aws_attach_user_group,
        "args": ["Service", "Group", "User"]
    },
    "DatabaseMigration": {
        "function": Database_Migration,
        "args": ["Schema_Name", "Associated_Runner", "Absolute_Dumpfile_Path", "Database_Name", "Source_Database",
                 "Destination_Database", "Directory", "Backup_Directory"]
    },
}


# Main Code
def main():
    while True:
        print_colored_text(text="Available functions:", color_code=YELLOW)
        for func_name, info in functions.items():
            arg_names = ", ".join(info["args"])
            print("- {} ({})".format(func_name, arg_names))
        print_colored_text(text="\nEnter 'exit' to quit", color_code=YELLOW)

        function_name = input("\nEnter the function name to execute: ")

        if function_name == 'exit':
            break

        selected_function_info = functions.get(function_name)
        if selected_function_info:
            selected_function = selected_function_info['function']
            args_info = selected_function_info['args']

            if args_info:
                args = []
                print_colored_text(text="\nArguments for {}:".format(function_name), color_code=YELLOW)
                for arg_name in args_info:
                    arg = input("Enter {}: ".format(arg_name))
                    args.append("{}='{}'".format(arg_name, arg))
                try:
                    selected_function(*args)
                    STACK_EMAIL(SUBJECT="{} Success!".format(selected_function),
                                BODY="This email is to let you know your function ran with no errors!",
                                TO_EMAIL="stackcloud11@mkitconsulting.net", COLOR=GREEN)
                except:
                    STACK_EMAIL(SUBJECT="{} Failure!".format(selected_function),
                                BODY="This email is to let you know your function ran with errors!",
                                TO_EMAIL="stackcloud11@mkitconsulting.net", COLOR=RED)
                break
            else:
                selected_function()
        else:
            print_colored_text(text="\nFUNCTION NOT FOUND. PLEASE ENTER A VALID FUNCTION NAME.\n", color_code=RED)


# MainBody
if __name__ == "__main__":
    main()

