#!/usr/bin/python
'''
dups=[1,1,2,2,3,3,4,4]
dedup=set(dups)
print(dedup)

cars={
	"Brand":"Honda",
	"Model":"Accord",
	"Year": 2010
}
print(cars["Brand"])
print(cars.get("Model"))

cars["Year"]=2023
print(cars)

cars={
   "Brand":"Honda",
   "Model":"Accord",
   "Year": 2010
}
for x in cars:
	print(x)

for x in cars:
	print(cars[x])

for x in cars.values():
	print(x)

for x,y in cars.items():
	print(x, "=>", y)

cars={
   "Brand":"Honda",
   "Model":"Accord",
   "Year": 2010
}

if "Brand" in cars:
	print("Brand Exist in car dict")

print(len(cars))
cars["Tag"]="15ABQ"
print(cars)

cars.pop("Tag")
print(cars)

cars["Tag"]="15ABQ"
cars.popitem()
print(cars)

cars={
   "Brand":"Honda",
   "Model":"Accord",
   "Year": 2010
}

del cars["Year"]
print(cars)

#del cars
#print(cars)

cars.clear()
print(cars)

cars={
   "Brand":"Honda",
   "Model":"Accord",
   "Year": 2010
}

cars2=cars.copy()
print(cars2)

cars3=dict(cars)
print(cars3)

car1 = {
   "Brand":"Honda",
   "Model":"Accord",
   "Year": 2010
}

car2 = {
   "Brand":"Toyota",
   "Model":"Camry",
   "Year": 2005
}

car3 = {
   "Brand":"Hyundai",
   "Model":"Elentra",
   "Year": 2023
}

cars = {
   "car1": car1,
	"car2": car2,
	"car3": car3
}

print(cars["car1"])

name="Michael"
if name == "Michael":
	pass

i = 1
while i < 6:
	print(i)
	i += 1

counter = 1
while counter < 6:
	print(counter)
	if counter == 3:
		break
	counter += 1

counter = 0
while counter <= 10:
	print(counter)
	if counter == 11:
		break
	counter += 1

emptylist = []
while 2 > 1:
	i = int(input("Input a number or something: "))
	emptylist.append(i)
	if i == 0:
		break
print(emptylist)

import os
import subprocess
dirpath = "/home/oracle/scripts/practicedir_myl_sep23/"
findfile = "testloop.txt"
pathfile = os.path.join(dirpath, findfile)
while 2 > 1:
	if os.path.isfile(pathfile):
		print("File Found! Breaking loop!")
		subprocess.run(["ls","-l",pathfile])
		break
	print("Searching for {} in {}!".format(findfile, dirpath))

i = 1
while i < 6:
	i += 1
	if i == 3:
		continue
	print(i)
'''
i = 1
while i < 6:
	print(i)
	i += 1
else:
	print("i is no longer less than 6")
	
		
	

	



