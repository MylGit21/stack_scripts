#!/usr/bin/python

# Modules
import sys as i
import os
import importlib
import stack_modules_v1_3 as s

# Variables
func = ""
if len(i.argv) >= 2:
    func = i.argv[1]
argus = len(i.argv) - 1


# Main Code
def main():
    while True:
        s.print_colored_text(text="Available functions:", color_code=s.YELLOW)
        for func_name, info in s.functions.items():
            arg_names = ", ".join(info["args"])
            print("- {} ({})".format(func_name, arg_names))
        s.print_colored_text(text="\nEnter 'exit' to quit", color_code=s.YELLOW)

        function_name = input("\nEnter the function name to execute: ")

        if function_name == 'exit':
            break

        selected_function_info = s.functions.get(function_name)
        if selected_function_info:
            selected_function = selected_function_info['function']
            args_info = selected_function_info['args']

            if args_info:
                args = {}
                s.print_colored_text(text="\nArguments for {}:".format(function_name), color_code=s.YELLOW)
                for arg_name in args_info:
                    arg = input("Enter {}: ".format(arg_name))
                    args[arg_name] = arg
                #try:
                print(*args)
                selected_function(**args)
                '''s.STACK_EMAIL(SUBJECT="{} Success!".format(selected_function),
                                  BODY="This email is to let you know your function ran with no errors!",
                                  TO_EMAIL="stackcloud11@mkitconsulting.net", COLOR=s.GREEN)
                except:
                    s.STACK_EMAIL(SUBJECT="{} Failure!".format(selected_function),
                                  BODY="This email is to let you know your function ran with errors!",
                                  TO_EMAIL="stackcloud11@mkitconsulting.net", COLOR=s.RED)'''
                break
            else:
                selected_function()
        else:
            s.print_colored_text(text="\nFUNCTION NOT FOUND. PLEASE ENTER A VALID FUNCTION NAME.\n", color_code=s.RED)


# MainBody
if __name__ == "__main__":
    if func != "":
        if func == "Backup":
            if argus == 3:
                src = i.argv[1]
                dst = i.argv[2]
                s.Backup(src=src, dst=dst)
            else:
                s.print_colored_text(text="\nFUNCTION VARIABLES NOT APPLICABLE. PROMPTING USAGE PROMPT.\n", color_code=s.RED)
                main()
        if func == "DatabaseBackup":
            if argus == 3:
                rnr = i.argv[1]
                sch = i.argv[2]
                s.DatabaseBackup(Associated_Runner=rnr, Schema_Name=sch)
            else:
                s.print_colored_text(text="\nFUNCTION VARIABLES NOT APPLICABLE. PROMPTING USAGE PROMPT.\n", color_code=s.RED)
                main()
        if func == "DatabaseImport":
            if argus == 4:
                sch = i.argv[1]
                rnr = i.argv[2]
                dmpath = i.argv[3]
                database = i.argv[4]
                s.DatabaseImport(Schema_Name=sch, Associated_Runner=rnr, Absolute_Dumpfile_Path=dmpath, Database=database)
            else:
                s.print_colored_text(text="\nFUNCTION VARIABLES NOT APPLICABLE. PROMPTING USAGE PROMPT.\n", color_code=s.RED)
                main()
        if func == "DatabaseMigration":
            if argus == 7:
                bckdir = i.argv[1]
                sch = i.argv[2]
                dstsch = i.argv[3]
                srcdb = i.argv[4]
                dstdb = i.argv[5]
                dir = i.argv[6]
                rnr = i.argv[7]
                s.Database_Migration(Backup_Directory=bckdir, Schema_Name=sch, Destination_Schema=dstsch, Source_Database=srcdb, Destination_Database=dstdb, Directory=dir, Associated_Runner=rnr)
            else:
                s.print_colored_text(text="\nFUNCTION VARIABLES NOT APPLICABLE. PROMPTING USAGE PROMPT.\n", color_code=s.RED)
                main()
        if func == "DiskCheck":
            if argus == 3:
                disk = i.argv[1]
                thrs = i.argv[2]
                s.Disk_Maintenance_Check_On_Prem(disk=disk, thrs=thrs)
            else:
                s.print_colored_text(text="\nFUNCTION VARIABLES NOT APPLICABLE. PROMPTING USAGE PROMPT.\n", color_code=s.RED)
                main()
        if func == "SendEmail":
            if argus == 4:
                SUBJECT = i.argv[1]
                BODY = i.argv[2]
                TO_EMAIL = i.argv[3]
                COLOR = s.YELLOW
                s.STACK_EMAIL(SUBJECT=SUBJECT, BODY=BODY, TO_EMAIL=TO_EMAIL, COLOR=COLOR)
            else:
                s.print_colored_text(text="\nFUNCTION VARIABLES NOT APPLICABLE. PROMPTING USAGE PROMPT.\n", color_code=s.RED)
                main()
        else:
            s.print_colored_text(text="\nFUNCTION NOT FOUND. PROMPTING USAGE PROMPT.\n", color_code=s.RED)
            main()
    else:
        s.print_colored_text(text="\nFUNCTION NOT FOUND. PROMPTING USAGE PROMPT.\n", color_code=s.RED)
        main()

