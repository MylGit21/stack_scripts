#!/usr/bin/python

#Modules
import sys as i
import shutil as c 
import os

#Variables
Src = i.argv[1]
Dst = i.argv[2]

#Functions
def Backup(Src,Dst):
	print("Backing up %s to %s"%(Src,Dst))
	
	#if src is a directory then copytree
	if os.path.isdir(Src):
		c.copytree(Src,Dst)
	else:
		c.copy(Src,Dst)
	
	#list files in dir
	print(Dst, "=", os.listdir(Dst))
	
#MainBody
if __name__ == "__main__":
	
	Backup(Src,Dst)
