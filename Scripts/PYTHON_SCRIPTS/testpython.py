#!/usr/bin/python

'''name = "Myles"
print("the length of my name is", len(name))
'''
'''b = "Myles "
print(b.strip())
'''
'''threshold ="65%"
if int(threshold.strip("%")) > 75:
	print("{} is greater than 75%".format(threshold))
else:
	print("{} is not greater than 75%".format(threshold))
'''
'''
b = "Myles"
print("My name in uppercase is", b.upper())
print("My name is lowercase is", b.lower())
'''
'''
a = "Stack"
print(a.replace("S","C"))
'''

'''
threshold = "65%"
if int(threshold.replace("%"," ")) > 75:
	print("Threshold is greater than 75%")
else:
	print("Threshold is less than 75%")
'''

'''
file1=open("testreplace.txt", "w+")
file1.write("baseball")
file1.close()
readfile1 = open("testreplace.txt", "r+")
print(readfile1.read().replace("baseball","basketball"))
'''

'''
file1=open("testreplace.txt", "w+")
file1.write("baseball")
file1.close()

file1 = open("testreplace.txt", "r+")
content=file1.read()
print("Original Content:", content)
newdata = content.replace("baseball","basketball")
file1.close()

file1 = open("testreplace.txt", "w+")
file1.write(newdata)
file1.close()

file1 = open("testreplace.txt", "r+")
print("New Content:", file1.read())
'''

'''
Fullname = "Myles Tucker"
Tokens = Fullname.split(" ")
print(Tokens[1])
'''

'''
disk = "/u01,/u02,/u03,/u04,/u05,/backup"
tokens=disk.split(",")
if tokens[5].strip("/") == "backup":
	print("Token 5 is backup")
else:
	print("Token 5 is NOT backup")
'''

'''
txt = "Stack IT training students stack up a lot of bread."
if "bread" in txt:
	print("Bread exist within statement")
'''

'''
txt = "Stack IT training students stack up a lot of bread."
if "Stack" in txt.title():
	cnt =  txt.title().count("Stack")
	print("Stack appears {} times.".format(cnt))
'''
'''
def my_function(*names):
	print("The youngest child is", names[2])	
my_function("Josh", "Jush", "Jash")
'''
'''
def hardadd(*args):
	a = 0
	for i in args:
		a = a + int(i)
	return a

print(hardadd(10,30,21,42))
'''
#Arbituary Args
'''
def add(*args):	
	return int(args[0])+int(args[1])

print(add(1, 2))
'''
'''
#Keyword Args
'''
'''
def my_function(name3,name1,name2):
	print("My name is", name1)
	
my_function(name1="Dude",name3="Bob",name2="Mike")
'''
'''
#Arbituary Keyword Args

def my_function(**names):
	print("Nick's last name is", names["lname"])
	print("Nicks first name is", names["fname"])

my_function(fname="Nick", lname="Moran")

txt="Myles said \"I like python!\" and I think he means it."
print(txt)
'''
name="myles"
print(name.capitalize())
