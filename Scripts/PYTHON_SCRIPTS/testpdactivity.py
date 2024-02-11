#!/usr/bin/python

#Imports
import cx_Oracle as cx


#Variable Decleration
OP_ID = 1
OP_NAME = "DATABASE_MIGRATION"



connection = cx.connect(user="STACK_MYL_SEP23", password="stackinc", dsn="MKIT-DEV-OEM/APEXDB")
print(connection.version)

cursor = connection.cursor()
cursor.execute("""insert into operations values(:OP_ID_INS, :OP_NAME_INS)""",
OP_ID_INS = OP_ID,
OP_NAME_INS = OP_NAME)

connection.commit()
