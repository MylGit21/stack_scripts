#!/usr/bin/python

#Modules
import sys as i
import shutil as c 

#Variables
Src = i.argv[1]
Dst = i.argv[2]

if __name__ == "__main__":
	print("Backing up %s to %s"%(Src,Dst))
	c.copy(Src,Dst,follow_symlinks=True)	

	print("FILES COPIED!!!")
