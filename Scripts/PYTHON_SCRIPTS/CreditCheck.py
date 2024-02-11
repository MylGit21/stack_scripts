#!/usr/bin/python


# Modules
import cx_Oracle as cx
import json

# Variables
JsonDataRef ="""
{
    "CreditCheck":[
        {
            "FNAME": "Lebron",
            "LNAME": "James",
            "AGE": 50,
            "SSN": "999-55-4444",
            "ADDRESS": "321 Lebron Ave"
        },
        {
            "FNAME": "Steph",
            "LNAME": "Curry",
            "AGE": 30,
            "SSN": "999-55-3333",
            "ADDRESS": "123 Curry Blvd"
        },
        {
            "FNAME": "Riley",
            "LNAME": "Freemen",
            "AGE": 12,
            "SSN": "999-55-2222",
            "ADDRESS": "118 Woody Ln"
        },
        {
            "FNAME": "Huey",
            "LNAME": "Freemen",
            "AGE": 12,
            "SSN": "999-55-1111",
            "ADDRESS": "118 Woody Ln"
        }
    ]
}"""
JsonData = json.loads(JsonDataRef)


# Functions
def Call2CreditCheck(ssn):
	for user in JsonData["CreditCheck"]:
		if user["SSN"] == ssn:
			connection = cx.connect(user="STACK_MYL_SEP23", password="stackinc", dsn="MKIT-DEV-OEM/APEXDB")
			cursor = connection.cursor()

			cursor.execute("SELECT CREDITSCORE FROM CREDITCHECK WHERE SSN = '{}'".format(ssn))
			results = cursor.fetchall()[0][0]
			return results, (user["FNAME"] + " " +  user["LNAME"])

# Main Runner
if __name__ == "__main__":
	ssn = input("Enter SSN to credit check: ")
	try:
		CS = Call2CreditCheck(ssn)
		print("User: ", CS[1], "\nCredit Score: ", CS[0])
		if CS[0] > 720:
			print("Approved!")
		else:
			print("Denied")
	except:
		print("INVALID SSN ENTERED! USER DOES NOT EXIST!")
