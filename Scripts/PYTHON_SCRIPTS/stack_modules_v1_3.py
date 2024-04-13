#!/usr/bin/python


# Modules
<<<<<<< HEAD
import boto3
=======
import boto3 
import botocore
>>>>>>> a4377f386df201c94742db02fb0bb7e496bd4b45
import gzip
import os
import psutil
import smtplib
import subprocess
import tarfile
import time
<<<<<<< HEAD
import shutil as s
import cx_Oracle as cx
=======
import json
import shutil as s
import cx_Oracle as cx 
>>>>>>> a4377f386df201c94742db02fb0bb7e496bd4b45
from pathlib import Path
from botocore.exceptions import ClientError

# Variables
RED = "\033[91m" # Error
YELLOW = "\033[93m" # Notification
BLUE = "\033[94m" # Header
GREEN = "\033[92m" # Success
MAGENTA = "\033[95m" # Logging



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

def aws_remove_usergroup(**kwargs):
    iam = boto3.client(service_name=kwargs["Service"])
    user_name = kwargs["User"]
    groups = iam.list_groups_for_user(UserName=user_name)["Groups"]
    for group in groups:
        iam.remove_user_from_group(GroupName=group["GroupName"], UserName=user_name)


def aws_assume_role(**kwargs):
    # This is being worked on still
    try:
        # Assume the specified IAM role using AWS security token service
        print('good1')
        sts_client = boto3.client('sts')
        print('good2')
        assumed_role = sts_client.assume_role(
            RoleArn="arn:aws:iam::730335539868:role/{}".format(kwargs['Role']),
            RoleSessionName=kwargs['Role_Session_Name'],
            DurationSeconds=kwargs.get('Duration_Seconds', 3600)
        )
        print("Assumed role '{}' for {} hours".format(kwargs['Role'], (assumed_role['Credentials']['Expiration']/3600)))
        print('good3')
        # Return the assumed role credentials
        return {
            'AccessKeyId': assumed_role['Credentials']['AccessKeyId'],
            'SecretAccessKey': assumed_role['Credentials']['SecretAccessKey'],
            'SessionToken': assumed_role['Credentials']['SessionToken']
        }

    except ClientError as error:
        print("Error assuming role: {}".format(error))
        print("Error response: {}".format(error.response))
        return None



def DB_Connection(**kwargs):
    # print(kwargs)
    connection = cx.connect(user="STACK_MYL_SEP23", password="stackinc", dsn="MKIT-DEV-OEM/APEXDB")
    # print_colored_text(text="Connection Version: {}".format(connection.version), color_code=YELLOW)

    cursor = connection.cursor()
    email = cursor.execute("SELECT MONITORING_EMAIL FROM PROD_OPERATIONS WHERE OP_ID = '{}'".format(kwargs["OP_ID"])).fetchall()[0][0]

    # If starttime but no endtime given do initial set up
    if "OP_STARTTIME" in kwargs and "OP_ENDTIME" not in kwargs:
        print_colored_text(text="FUNCTION LOGGED!", color_code=MAGENTA)
        cursor.execute("""INSERT INTO PROD_ACTIVITIES VALUES (:OP_ID_INS, :OP_STARTTIME_INS, :OP_ENDTIME_INS, :RUNNER_INS, :STATUS_INS, :MON_EMAIL_INS)""",
                            OP_ID_INS=kwargs["OP_ID"],
                            OP_STARTTIME_INS=kwargs["OP_STARTTIME"],
                            OP_ENDTIME_INS=kwargs["OP_STARTTIME"],
                            RUNNER_INS=kwargs["RUNNER"],
                            STATUS_INS=kwargs["STATUS"],
                            MON_EMAIL_INS=email)
    # If endtime but not starttime given update the initial set up
    elif 'OP_ENDTIME' in kwargs and 'OP_STARTTIME' not in kwargs:
        print_colored_text(text="LOG UPDATED!", color_code=MAGENTA)
        cursor.execute("update PROD_ACTIVITIES set OP_ENDTIME = :OP_ENDTIME_INS, STATUS = :STATUS_INS where STATUS = 'RUNNING' and RUNNER = :RUNNER_INS and OP_ID = :OP_ID_INS""",
                       OP_ENDTIME_INS=kwargs["OP_ENDTIME"],
                       STATUS_INS=kwargs["STATUS"],
                       RUNNER_INS=kwargs["RUNNER"],
                       OP_ID_INS=kwargs["OP_ID"])
    # If both endtime and starttime set for manual logging
    elif 'OP_ENDTIME' in kwargs and 'OP_STARTTIME' in kwargs:
        print_colored_text(text="FUNCTION LOGGED!", color_code=MAGENTA)
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


def fetchusers(**kwargs):
<<<<<<< HEAD
=======
    DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_STARTTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="RUNNING")
>>>>>>> a4377f386df201c94742db02fb0bb7e496bd4b45
    try:
        # Establish a connection to the Oracle database
        connection = cx.connect(user="STACK_MYL_SEP23", password="stackinc", dsn="MKIT-DEV-OEM/APEXDB")
        print("Connection Version: {}".format(connection.version))

        # Create a cursor to execute SQL statements
        cursor = connection.cursor()

        # Execute a query to fetch users ending with the specified suffix
        query = "SELECT username FROM all_users WHERE username LIKE '%{}'".format(kwargs["Suffix"])
        cursor.execute(query)

        # Fetch all the rows
        rows = cursor.fetchall()

<<<<<<< HEAD
        # Create group
        aws_create_group(Service="iam", Group="CLOUD_ENG")

        # Print the usernames
        for row in rows:
            print("Found user: {}".format(row[0]))
            aws_create_user(Service="iam", User="{}".format(row[0]))
            aws_attach_user_group(Service="iam", Group="CLOUD_ENG", User="{}".format(row[0]))
=======
        # Print the usernames
        for row in rows:
            print("Found user: {}".format(row[0]))
            aws_attach_user_group(Service=kwargs["Service"], Group=kwargs["Group"], User="{}".format(row[0]), Linked=True)
>>>>>>> a4377f386df201c94742db02fb0bb7e496bd4b45

        # Close the cursor and connection
        cursor.close()
        connection.close()
<<<<<<< HEAD

    except cx.Error as e:
        print("An error occurred:", e)
=======
        DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="COMPLETED")

    except cx.Error as e:
        print("An error occurred:", e)
        DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="ERROR")
        raise ValueError("Unexpected error occurred while fetching users")

>>>>>>> a4377f386df201c94742db02fb0bb7e496bd4b45


def aws_create_user(**kwargs):
    if not kwargs.get("Linked", False):
        DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_STARTTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="RUNNING")
<<<<<<< HEAD
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
=======

    try:
        iam = boto3.client(service_name=kwargs["Service"])
        re = iam.create_user(UserName=kwargs["User"])
        print_colored_text(text="User Creation Success!", color_code=GREEN)
        return kwargs["User"]  # Return the created user name
    
    # User already exist
    except ClientError as error:
        print_colored_text(text=error.response, color_code=RED)
        if error.response["Error"]["Code"] == "EntityAlreadyExists":
            
            # If function is linked auto-pass
            if not kwargs.get("Linked", False):
                print("User already exists.. Automatically using the same user.")
                val = 'y'
            else:
                print("User already exists.. Use the same user?")
                val = input("Enter (y or n): ")

            if val == 'y':
>>>>>>> a4377f386df201c94742db02fb0bb7e496bd4b45
                if not kwargs.get("Linked", False):
                    DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="COMPLETED")
                return kwargs["User"]
            else:
<<<<<<< HEAD
                print("You want to create a new user")
                new_user = input("Enter username: ")
                response = iam.create_user(UserName=new_user)
                print_colored_text(text="Success!", color_code=GREEN)
                if not kwargs.get("Linked", False):
                    DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="COMPLETED")
                return new_user
=======
                # Prompt creation of a diff username
                print("You want to create a new user")
                new_user = input("Enter username: ")
                response = iam.create_user(UserName=new_user)
                print_colored_text(text="User Creation Success!", color_code=GREEN)
                if not kwargs.get("Linked", False):
                    DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="COMPLETED")
                return new_user # Return the created user name
>>>>>>> a4377f386df201c94742db02fb0bb7e496bd4b45
        else:
            if not kwargs.get("Linked", False):
                DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="ERROR")
            raise ValueError("Unexpected error occurred while creating user")


<<<<<<< HEAD
=======
def aws_delete_user(**kwargs):
    try:
        iam = boto3.client(service_name=kwargs["Service"])
        user_name = kwargs["User"]
        suffix = kwargs.get("Suffix", "")

        if suffix:
            # If Suffix is provided, delete all users with the specified suffix
            response = iam.list_users()
            users_to_delete = [user["UserName"] for user in response["Users"] if suffix in user["UserName"]]

            if not users_to_delete:
                print_colored_text(text="No users with suffix '{}' found.".format(suffix), color_code=RED)
                return

            for user in users_to_delete:
                aws_remove_usergroup(User=user,Service=kwargs["Service"])
                try:
                    iam.delete_login_profile(UserName=user)
                    print_colored_text(text="Login profile deleted for user '{}'.".format(user), color_code=GREEN)
                except ClientError as login_error:
                    if login_error.response["Error"]["Code"] == "NoSuchEntity":
                        pass  # No login profile exists, continue with deletion
                iam.delete_user(UserName=user)
            print_colored_text(text="Users with the '{}' suffix deleted.".format(suffix), color_code=GREEN)

        else:
            # If Suffix is not provided, delete the specified user
            aws_remove_usergroup(User=kwargs["User"],Service=kwargs["Service"])
            try:
                iam.delete_login_profile(UserName=kwargs["User"])
                print_colored_text(text="Login profile deleted for user '{}'.".format(user), color_code=GREEN)
            except ClientError as login_error:
                if login_error.response["Error"]["Code"] == "NoSuchEntity":
                    pass  # No login profile exists, continue with deletion
            iam.delete_user(UserName=user_name)
            print_colored_text(text="User '{}' deleted.".format(user_name), color_code=GREEN)

    except ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchEntity":
            print_colored_text(text="User '{}' does not exist.".format(user_name), color_code=RED)
        else:
            print_colored_text(text="Error: {}".format(error.response['Error']['Message']), color_code=RED)


>>>>>>> a4377f386df201c94742db02fb0bb7e496bd4b45
def aws_create_group(**kwargs):
    admin_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
    if not kwargs.get("Linked", False):
        DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_STARTTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="RUNNING")
<<<<<<< HEAD
=======

>>>>>>> a4377f386df201c94742db02fb0bb7e496bd4b45
    try:
        iam = boto3.client(service_name=kwargs["Service"])
        group_name = kwargs["Group"]

        try:
            # Check if the group already exists
            iam.get_group(GroupName=group_name)

<<<<<<< HEAD
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
            if not kwargs.get("Linked", False):
                DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="COMPLETED")

        except ClientError as group_error:
            if group_error.response["Error"]["Code"] == "NoSuchEntity":
                # Group doesn't exist, create it
                response = iam.create_group(GroupName=group_name)
                print(response)
                print_colored_text(text="Success!", color_code=GREEN)
=======
            if not kwargs.get("Linked", False):
                print_colored_text(text="Group '{}' already exists.".format(group_name), color_code=RED)
                print("Do you want to use the same group?")
                val = input("Enter (y or n): ")
                if val.lower() == 'y':
                    print("You want to use the same group")
                    pass
                else:
                    # Prompt creation of a diff group
                    print("You want to create a new group")
                    new_group = input("Enter group name: ")
                    response = iam.create_group(GroupName=new_group)
                    print_colored_text(text="Group Creation Success!", color_code=GREEN)
            else:
                print_colored_text(text="Group '{}' already exists.".format(group_name), color_code=RED)
                print("Automatically using the same group.")
                val = 'y'

            # Check if the admin policy is attached to the group
            attached_policies = iam.list_attached_group_policies(GroupName=group_name)['AttachedPolicies']
            admin_policy_attached = any(policy['PolicyArn'] == admin_policy_arn for policy in attached_policies)

            # Attach the admin policy to the group if not already attached
            if not admin_policy_attached:
                iam.attach_group_policy(GroupName=group_name, PolicyArn=admin_policy_arn)
                print_colored_text(text="Admin policy attached to the group '{}'.".format(group_name), color_code=YELLOW)

            if not kwargs.get("Linked", False):
                DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="COMPLETED")

        # Group doesn't exist, create it
        except ClientError as group_error:
            if group_error.response["Error"]["Code"] == "NoSuchEntity":
                response = iam.create_group(GroupName=group_name)
                print_colored_text(text="Group Creation Success!", color_code=GREEN)
>>>>>>> a4377f386df201c94742db02fb0bb7e496bd4b45

                # Attach the admin policy to the newly created group
                iam.attach_group_policy(GroupName=group_name, PolicyArn=admin_policy_arn)
                print_colored_text(text="Admin policy attached to the group '{}'.".format(group_name), color_code=YELLOW)
                if not kwargs.get("Linked", False):
                    DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="COMPLETED")

            else:
                print_colored_text(text=group_error.response, color_code=RED)
                if not kwargs.get("Linked", False):
                    DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="ERROR")
                raise ValueError("Unexpected error occurred while creating group")

    except ClientError as error:
        print_colored_text(text=error.response, color_code=RED)
        if not kwargs.get("Linked", False):
            DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="ERROR")
        raise ValueError("Unexpected error occurred while creating group")


def aws_attach_user_group(**kwargs):
<<<<<<< HEAD
    DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_STARTTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="RUNNING")
=======
    if not kwargs.get("Linked", False):
        DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_STARTTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="RUNNING")
>>>>>>> a4377f386df201c94742db02fb0bb7e496bd4b45
    try:
        iam = boto3.client(service_name=kwargs["Service"])
        user_name = aws_create_user(Service=kwargs["Service"], User=kwargs["User"], Linked=True)
        group_name = kwargs["Group"]

        # Check if the group exists and create it if needed
        aws_create_group(Service=kwargs["Service"], Group=group_name, Linked=True)

        # Attach the user to the group
        iam.add_user_to_group(GroupName=group_name, UserName=user_name)
        print_colored_text(text="User '{}' attached to group '{}'.".format(user_name, group_name), color_code=GREEN)

        # Set up login profile for the user
<<<<<<< HEAD
        pswrd = input("Enter password for user '{}': ".format(user_name))
        iam.create_login_profile(UserName=user_name, Password=pswrd)
        print_colored_text(text="Login profile created for user '{}'.".format(user_name), color_code=GREEN)
        DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="COMPLETED")

    except ClientError as error:
        print_colored_text(text="Error: {}".format(error.response['Error']['Message']), color_code=RED)
        DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="ERROR")
=======
        pswrd = "ChangeMe123!"
        iam.create_login_profile(UserName=user_name, Password=pswrd,  PasswordResetRequired=True)
        print_colored_text(text="Login profile created for user '{}'.".format(user_name), color_code=GREEN)
        if not kwargs.get("Linked", False):
            DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="COMPLETED")

    except ClientError as error:
        print_colored_text(text="Error: {}".format(error.response['Error']['Message']), color_code=RED)
        if not kwargs.get("Linked", False):
            DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="ERROR")


def create_s3_bucket(**kwargs):
    try:
        s3 = boto3.client(service_name=kwargs["Service"])
        # If Role is not defined ignore role assumption.
        if kwargs.get("Role", False):
            aws_assume_role(Role=kwargs["Role"], Role_Session_Name=kwargs["Role_Session_Name"], Duration_Seconds=int(kwargs["Duration_Seconds"]))

        # Create an S3 bucket
        s3.create_bucket(Bucket=kwargs['Bucket_Name'])
        print("S3 bucket '{}' created successfully.".format(kwargs['Bucket_Name']))

    except ClientError as error:
        print("Error creating S3 bucket: {}".format(error))
    except Exception as e:
        print_colored_text(text="Error: {}".format(e), color_code=RED)
        if not kwargs.get("Linked", False):
            DB_Connection(OP_ID=6, OP_NAME="IAM", OP_TYPE="AWS", OP_ENDTIME=time.strftime('%d-%b-%y %I.%M.%S %p'), RUNNER="MYLES", STATUS="ERROR")
    

>>>>>>> a4377f386df201c94742db02fb0bb7e496bd4b45


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
    "File Mangement Functions": {
        "Backup": {
            "function": Backup,
            "args": ["Source", "Destination"]
        },
        "DatabaseBackup": {
            "function": DatabaseBackup,
            "args": ["Associated_Runner", "Schema_Name"]
        },
        "DatabaseImport": {
            "function": DatabaseImport,
            "args": ["tarfile", "Schema_Name", "BackupLocation", "DatabaseName", "Runner", "ConfigPath", "Directory"]
        },
        "DatabaseMigration": {
            "function": Database_Migration,
            "args": ["Schema_Name", "Associated_Runner", "Absolute_Dumpfile_Path", "Database_Name", "Source_Database",
                    "Destination_Database", "Directory", "Backup_Directory"]
        },
        "UnGzip": {
            "function": UnGzip,
            "args": ["Absolute_Path"]
        },
    },
    "AWS Functions": {
        "aws_create_user": {
            "function": aws_create_user,
            "args": ["Service", "User"]
        },
        "aws_delete_user": {
            "function": aws_delete_user,
            "args": ["Service", "User","Suffix"]
        },
        "aws_create_group": {
            "function": aws_create_group,
            "args": ["Service", "Group"]
        },
        "aws_attach_user_group": {
            "function": aws_attach_user_group,
            "args": ["Service", "Group", "User"]
        },
        "aws_assume_role": {
            "function": aws_assume_role,
            "args": ["Role", "Role_Session_Name", "Duration_Seconds"]
        },
        "create_s3_bucket": {
            "function": create_s3_bucket,
            "args": ["Service", "Bucket_Name", "Role", "Role_Session_Name", "Duration_Seconds"]
        },
    },
    "Disk/Logging Functions": {
        "DB_Connection": {
            "function": DB_Connection,
            "args": ["OP_ID", "OP_NAME", "OP_TYPE", "OP_STARTTIME", "RUNNER", "STATUS", "MON_EMAIL", "OP_ENDTIME"]
        },
        "SmartDiskMonitor": {
            "function": SmartDiskMonitor,
            "args": ["Disk"]
        },
        "DiskCheck": {
            "function": Disk_Maintenance_Check_On_Prem,
            "args": ["Disk", "Threshold"]
        },
        "StackEmail": {
            "function": STACK_EMAIL,
            "args": ["SUBJECT", "BODY", "TO_EMAIL"]
        },
    },
<<<<<<< HEAD
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
    "fetchusers": {
        "function": fetchusers,
        "args": ["Suffix", "Service", "Group"]
    },
    "DatabaseMigration": {
        "function": Database_Migration,
        "args": ["Schema_Name", "Associated_Runner", "Absolute_Dumpfile_Path", "Database_Name", "Source_Database",
                 "Destination_Database", "Directory", "Backup_Directory"]
=======
    "One-Time Specific Functions": {
        "AWS fetchusers": {
            "function": fetchusers,
            "args": ["Suffix", "Service", "Group"]
        },
>>>>>>> a4377f386df201c94742db02fb0bb7e496bd4b45
    },
}


# Main Code
def main():
    while True:
        print_colored_text(text="Available functions:", color_code=BLUE)
         
        for category, functions_in_category in functions.items():
            print_colored_text(text="\n{}:".format(category), color_code=YELLOW)
            
            for function_name, info in functions_in_category.items():
                arg_names = ", ".join(info["args"])
                print("- {} ({})".format(function_name, arg_names))

        function_name = input("\nEnter the function name to execute: ")

        if function_name == "exit":
            break
    
        selected_function_info = None
        for functions_in_category in functions.values():
            selected_function_info = functions_in_category.get(function_name)
            if selected_function_info:
                break

        if selected_function_info:
            selected_function = selected_function_info['function']
            args_info = selected_function_info['args']

            if args_info:
                kwargs = {}
                print_colored_text(text="\nArguments for {}:".format(function_name), color_code=YELLOW)
                for arg_name in args_info:
                    arg = input("Enter {}: ".format(arg_name))
                    kwargs[arg_name] = arg
                try:
                    selected_function(**kwargs)
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
