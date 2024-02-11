#!/usr/bin/python

#Modules
import shutil as c

#Variables
Src = "/home/oracle/scripts/practicedir_myl_sep23/Python/test"
Dst = "/home/oracle/scripts/practicedir_myl_sep23/Python/test2"


if __name__ == "__main__":
	print("Backing up %s to %s"%(Src,Dst))
	c.copy(Src,Dst)
	
	print("Files Backed Up!")
