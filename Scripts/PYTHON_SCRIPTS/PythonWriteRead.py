#!/user/bin/python


"""
user_entry=input("Please Enter Name: ")
print("User Entered: {}".format(user_entry))
print(type(user_entry))


for x in range(2,10):
	print(x)

for x in range(2,10,2):
	print(x)
"""

#Creating/Writing into a file
fo = open("test_myles.par","w+")
print("The name of the file is {}".format(fo.name))
print("Is {} closed? Answer: {}".format(fo.name, fo.closed))
fo.write("userid='/ as sysdba'\nschemas = stack_temp\ndumpfile=stack_temp_myl123456.dmp\nlogfile=stack_temp_myl123456.log\ndirectory=DATA_PUMP_DIR")
fo.close()
print("Is {} closed? Answer: {}".format(fo.name, fo.closed))

#OPening and Reading from a file
file_read=open("test_myles.par","r+")
file_content=file_read.read()
print(file_content)
file_read.close()


