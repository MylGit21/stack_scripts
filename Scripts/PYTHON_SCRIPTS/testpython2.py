#!/usr/bin/python

import sys as i


def Add(**argus):
	return int(argus["value1"]) + int(argus["value2"])

def Sub(**argus):
	return int(argus["value1"]) - int(argus["value2"])

def Mult(**argus):
	return int(argus["value1"]) * int(argus["value2"])

Function = input("Functions:\nAdd\nSub\nMult\nEnter what function you want to run: ")
x = input("Input first number: ")
y = input("Input second number: ")

print("Calling {} function!".format(Function))

if Function == "Add":
	print(Add(value1="{}".format(x),value2="{}".format(y)))
elif Function == "Sub":
	print(Sub(value1="{}".format(x),value2="{}".format(y)))
elif Function == "Mult":
	print(Mult(value1="{}".format(x),value2="{}".format(y)))


