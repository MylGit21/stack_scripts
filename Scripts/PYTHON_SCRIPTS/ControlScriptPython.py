#!/usr/bin/python

#Import Modules
import StackModules as m
import sys as i



#Variables
hostname=input("Please enter the Host Server: ")

#MainBody
if __name__ == "__main__":
	dict=m.GetDictionaries()

	#print(dict["Hosts"][0][hostname])

	for hostdict in dict["Hosts"]:
		for key, value in hostdict.items():
			if key == hostname:
				print('Server Type: %s' %value)
				break




	#print("Answer:", func_dict[fnc](x,y))
