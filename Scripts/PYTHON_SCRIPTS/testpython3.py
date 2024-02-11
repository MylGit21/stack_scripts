#!/usr/bin/python
'''
names=["Myles","Mike","Person"]
print(len(names))
names=["Myles","Mike","Charles","Yinka","Nick","Ola"]
names.append("Ross")
names.insert(3,"Elaine")
names.remove("Charles")
names.pop()
names.pop(0)
del names[0]
print(names)
print(len(names))
print("clearing the list")
names.clear()
print(names)

names=["Myles","Mike","Charles","Yinka","Nick","Ola"]
names2=names.copy()
print(names2)

names=["Myles","Mike","Charles","Yinka","Nick","Ola"]
names2=["Wilson","Uche","Remi"]
#names3=names+names2
#print(names3)

for x in names2:
	names.append(x)
print(names)

names=["Myles","Mike","Charles","Yinka","Nick","Ola"]
names2=["Wilson","Uche","Remi"]
names.extend(names2)
print(names)

names=list(("Myles","Mike","Charles","Yinka","Nick","Ola"))
print(names)
'''
numbers=[1,1,2,2,3,4,5,6,6,7,8,9,9,10]
dups=[]
for number in numbers:
	if numbers.count(number) > 1:
		dups.append(number)
print("The dups are",set(dups))


