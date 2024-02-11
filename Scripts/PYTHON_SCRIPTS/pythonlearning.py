#!/usr/bin/python

#Modules
import sys as i
import shutil as c 
import os

#Variables
func = i.argv[1]





#Functions
def Backup(Src,Dst):
	print("Backing up %s to %s"%(Src,Dst))
	
	#if src is a directory then copytree
	if os.path.isdir(Src):
		c.copytree(Src, os.path.join(Dst, Src))
	else:
		c.copy(Src,Dst)
	
	#list files in dir
	print(Dst, "=", os.listdir(Dst))


def CopyOver(Src,Dst):
	print("Copying contents from %s to %s"%(Src,Dst))

	confirm = input("Type 'Yes' to Confirm!")
	if confirm == "Yes":
		c.copyfile(Src,Dst)
	


#MainBody
if __name__ == "__main__":
	if func=="Backup":
		Backup(Src,Dst)
	elif func== "CopyOver":
		CopyOver(Src,Dst)
	else:
		print("Invalid Function! Please enter one of the following.\nBackup\nCopyOver")
