#!/usr/bin/python

# Modules
import os, time, subprocess, psutil, gzip, tarfile, smtplib
import shutil
import sys as i
import shutil as c
from pathlib import Path

# Variables
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"


# Sub Functions
def print_colored_text(**args):
    print("{}{}\033[0m".format(args["color_code"], args["text"]))


def STACK_EMAIL(**args):
    args["FROM"] = "oracle@MKIT-DEV-OEM.localdomain"
    args["MSG"] = ("\n".join(
        ("From: {}".format(args["FROM"]), "To: {}".format(args["TO_EMAIL"]), "Subject: {}\n".format(args["SUBJECT"]), "{}".format(args["BODY"]))))
    with smtplib.SMTP('localhost') as my_server:
        my_server.sendmail(args["FROM"], args["TO_EMAIL"], args["MSG"])
        print_colored_text(text="Email sent successfully to %s" % args["TO_EMAIL"], color_code=args["COLOR"])


def Gzip(**args):
    print_colored_text(text="Zipping {} to {}!".format(args["Src"], args["Dst"]), color_code=YELLOW)

    try:
        # if path is a file normally gzip
        if os.path.isfile(args["Src"]):
            print("Source is a file!")
            with open(args["Src"], 'rb') as Ginput:
                with gzip.open("{}.gz".format(args["Src"]), 'wb') as Goutput:
                    Goutput.writelines(Ginput)
                    print_colored_text(text="Zipping {} to {} was successful!".format(args["Src"], args["Dst"]), color_code=GREEN)
        # if path is a directory, use tar.gz
        elif os.path.isdir(args["Src"]):
            print("Source is a directory!")
            with tarfile.open("{}.tar.gz".format(args["Src"]), "w:gz") as tar:
                tar.add(args["Src"])
                print_colored_text(text="Tar Zipping {} to {} was successful!".format(args["Src"], args["Dst"]), color_code=GREEN)
        else:
            print_colored_text(text="File is neither a file or directory!", color_code=RED)
    except:
        print_colored_text(text="FAILED TO GZIP {}".format(args["Src"]), color_code=RED)
        raise ValueError("Gzip Failed")


def list_files_in_directory(**args):
    path = Path(args["directory"])
    print_colored_text(text="\n{} contents: ".format(args["directory"]), color_code=YELLOW)
    for file in path.iterdir():
        print(file.name)


# Primary Functions
def Backup(**args):
    print_colored_text(text="Backing up %s to %s" % (args["Source"], args["Destination"]), color_code=YELLOW)
    try:
        # check for timestamp
        TS = input("\nAdd a timestamp? (Leave blank for no): ")
        if TS != "":
            TS = time.strftime("%d%m%Y%H%M", time.localtime())

        # if src is a directory then copytree
        if os.path.isdir(args["Source"]):
            c.copytree(args["Source"], os.path.join(args["Destination"], args["Source"] + TS))
            print_colored_text(text="Successfully copied {} to {}!".format(args["Source"] + TS, args["Destination"]), color_code=GREEN)
        else:
            c.copy(args["Source"], os.path.join(args["Destination"], args["Source"] + TS))
            print_colored_text(text="Successfully copied {} to {}!".format(args["Source"] + TS, args["Destination"]), color_code=GREEN)

        # check for zip
        ZG = input("\nZip this file/directory? (Leave blank for no): ")
        if ZG != "":
            # gzip the file
            Gzip(Src=os.path.join(args["Destination"], args["Source"] + TS), Dst=args["Destination"])

            if os.path.isfile(args["Source"]):
                os.remove(os.path.join(args["Destination"], args["Source"] + TS))
            elif os.path.isdir(args["Source"]):
                shutil.rmtree(os.path.join(args["Destination"], args["Source"] + TS))

        # list new files in directory
        list_files_in_directory(args["Destination"])
    except:
        print_colored_text(text="Failed to backup %s to %s" % (args["Source"], args["Destination"]), color_code=RED)
        raise ValueError("Backup Failed")


def UnGzip(**args):
    print_colored_text(text="Unzipping {}!".format(args["Absolute_Path"]), color_code=YELLOW)
    try:
        tar = tarfile.open(args["Absolute_Path"])
        tar.extractall()
        tar.close
    except:
        print("Could not unzip file")
    dmpfiletest = os.path.splitext(args["Absolute_Path"])[0]
    dmpfile = (os.path.basename(args["Absolute_Path"]))
    print(dmpfile)
    return dmpfile


def Disk_Maintenance_Check_On_Prem(**args):
    try:
        # get disk usage using psutil
        disk_usage = psutil.disk_usage(args["Disk"])

        # extract the usage percentage
        usage_percent = disk_usage.percent

        # Check if the disk utilization exceeds the threshold
        if int(usage_percent) > int(args["Threshold"]):
            print("Disk utilization threshold breached for {}. Current utilization: {}".format(args["Disk"], usage_percent))
        else:
            print("Disk utilization within threshold for {}. Current utilization: {}".format(args["Disk"], usage_percent))
    except:
        print("Failed to check disk usage")
        raise ValueError("Disk Check Failed")


def DatabaseBackup(**args):
    TS = time.strftime("%d%m%Y%H%M%S", time.localtime())
    backup_base = "/backup/AWSSEP23/APEXDB/SAMD"
    backup_dir = os.path.join(backup_base, args["Associated_Runner"])

    try:
        file = open("/home/oracle/scripts/practicedir_myl_sep23/export_stack_temp_{}.par".format(TS), "w+")
        file.write("userid='/ as sysdba'\nschemas={}\ndumpfile=stack_temp_{}.dmp\nlogfile=stack_temp_{}.log\ndirectory=DATA_PUMP_DIR".format(args["Schema_Name"], TS, TS))
        file.close()

        file_read = open("/home/oracle/scripts/practicedir_myl_sep23/export_stack_temp_{}.par".format(TS), "r+")
        file_content = file_read.read()

        print(file_content)
        file_read.close()
        file_name = "export_stack_temp_{}.par".format(TS)
        file_path = os.path.join("/home/oracle/scripts/practicedir_myl_sep23", "{}".format(file_name))
        print_colored_text(file_path, RED)

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
    except:
        print("Export Failed")
        raise ValueError("DataBase Backup Failed")


def DatabaseImport(**args):
    TS = time.strftime("%d%m%Y%H%M%S", time.localtime())

    Directory = "/home/oracle/scripts/practicedir_myl_sep23"
    ConfigPath = "{}/impdp_{}_{}.par".format(Directory, args["Schema_Name"], args["Destination_Schema"])
    DestinationPath = "/backup/AWSSEP23/SAMD"

    try:
        AbsolutePath = "{}/{}".format(args["Backup_Directory"], args["DumpFile"])
        print("Unzipping absolute path:", AbsolutePath)
        UnGzip(AbsolutePath)
        UnzippedFile = "{}".format(args["DumpFile"][:-3])
        print("Unzipped file:", UnzippedFile)

        config = "userid='/ as sysdba'\nschemas={}\nremap_schema={}:%s_MIGRATED\ndumpfile={}\nlogfile=impdp_{}_{}.log\ndirectory={}\ntable_exists_action=replace".format(args["Schema_Name"], args["Schema_Name"], args["Destination_Schema"], UnzippedFile, args["Schema_Name"], args["Destination_Schema"], args["Directory"])

        #Writing into the par file
        parfile = open(ConfigPath, "w+")
        parfile.write("{}".format(config))
        parfile.close()

        parfile = open(ConfigPath, "r+")
        parcontent = parfile.read()
        print(parcontent)
        parfile.close()

        #Creating import sh file
        importsh = open("{}/import.sh".format(Directory), "w+")
        importsh.write(". /home/oracle/scripts/oracle_env_{}.sh\nimpdp parfile={}".format(args["Database_Name"],ConfigPath))
        importsh.close()
        importcontent = "{}/import.sh".format(Directory)
        print(importcontent)

        UnzippedFilePath = "{}/{}".format(args["Backup_Directory"], UnzippedFile)

        #Copying unzipped file into SAMD db
        shutil.copy(UnzippedFilePath,DestinationPath)

        #Granting permissions to run import file
        os.popen("chmod 700 {}".format(importcontent))
        subprocess.run(["/bin/bash", importcontent], check=True)

        #Opening logfile in read mode
        importlogfile = "impdp_{}_{}.log".format(args["Schema_Name"],args["Destination_Schema"])
        importlogfilepath = os.path.join(DestinationPath,importlogfile)

        with open(importlogfilepath, "r") as import_logfile:
            logcontent = importlogfile.read()
            print(logcontent)

        if "successfully completed" in logcontent:
            print("Import Success!")
        else:
            print("Import Failure!")
    except Exception as e:
        print(e)


def Database_Migration(**args):
    TS = time.strftime("%d%m%Y%H%M%S", time.localtime())

    #Setting Variables
    filefig = "userid='/ as sysdba'\nschemas=%s\nremap_schema={}:{}_{}_MIGRATED\ndumpfile={}_{}_{}.dmp\nlogfile=impdp_{}_{}.log\ntable_exist_action=replace".format(args["Schema_Name"], args["Schema_Name"], args["Schema_Name"], args["Associated_Runner"], args["Schema_Name"], args["Associated_Runner"], TS, args["Schema_Name"], args["Destination_Schema"], args["Directory"])
    local_dir = "/home/oracle/scripts/practicedir_myl_sep23"
    config_file_path = "{}/impdp_{}_{}_{}.par".format(local_dir, args["Schema_Name"], args["Destination_Schema"], TS)
    dumpfile_path = "{}/{}_{}_{}.dmp".format(args["Backup_Directory"], args["Schema_Name"], args["Associated_Runner"], TS)
    dest_dump_path = "/backup/AWSSEP23/{}".format(args["Destination_Database"])
    args["Absolute_Dumpfile_Path"] = dumpfile_path
    try:
        DatabaseBackup(**args)

        Absolute_Path = "{}/{}_{}_{}.dmp.gz".format(args["Backup_Directory"], args["Schema_Name"], args["Associated_Runner"], TS)
        print("Absolute path before unzipping:", Absolute_Path)

        UnGzip(Absolute_Path)

        #Writing the config par file
        par = open(config_file_path, "w+")
        print("File name is:", par.name)
        par.write("{}".format(filefig))
        par.close()

        par = open(config_file_path, "r+")
        file_content = par.read()
        par.close()

        impor = open("{}/import.sh".format(local_dir), "w+")
        impor.write(". /home/oracle/scripts/oracle_env_{}.sh\nimpdp parfile={}".format(args["Destination_Database"], config_file_path))
        impor.close()
        impor_content = "{}/import.sh".format(local_dir)
        print(impor_content)

        #Copying unzipped dump file
        shutil.copy(dumpfile_path, dest_dump_path)

        os.popen("chmod 700 {}".format(impor_content))
        os.popen("{}".format(impor_content))

    except Exception as e:
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
    "DiskCheck": {
        "function": Disk_Maintenance_Check_On_Prem,
        "args": ["Disk", "Threshold"]
    },
    "UnGzip": {
        "function": UnGzip,
        "args": ["Absolute_Path"]
    },
    "DatabaseImport": {
        "function": DatabaseImport,
        "args": ["Backup_Directory", "Schema_Name", "Destination_Schema", "Source_Database", "Destination_Database", "Directory", "Associated_Runner"]
    },
    "StackEmail": {
        "function": STACK_EMAIL,
        "args": ["SUBJECT", "BODY", "TO_EMAIL"]
    },
    "DatabaseMigration": {
        "function": Database_Migration,
        "args": ["Schema_Name", "Associated_Runner", "Absolute_Dumpfile_Path", "Database_Name", "Source_Database", "Destination_Database", "Directory", "Backup_Directory"]
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

