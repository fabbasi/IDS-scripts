#!/usr/bin/env python

###################################
# Author: Fahim Abbasi
# Date: 20111117
# Description: The make_labelled_binaries scripts job is to prepare a dataset of labelled binaries from tillmanns dataset. The labels are assigned to the name of the file prepended with the md5hash.
###################################

import sys
import os
import time
import re
#import spamsum
import errno
import hashlib
import csv

print "2 arguments required <file list> <target dataset directory/>"

filelist = sys.argv[1]
datasetdir = sys.argv[2]

#reportdir = "./report"

flist = list()
f = open(filelist,"r")
for line in f.xreadlines():
        line = line.strip('\n')
        flist.append(line)
        print line
f.close()

#inc = 0
#while "0" in pathstr:
try:
	os.makedirs("./binary")
except os.error, e:
	if e.errno != errno.EEXIST:
		raise

listing = os.listdir(datasetdir)
selection = [] 
count = 1
print "List length= ", len(listing)
for infile in flist:
		print "Current file is: " + datasetdir + infile
#		print "File Submitted Successfully"
	#temphash = infile.split(".")	
		myfile =  datasetdir + infile
	#	fhash = temphash[0]
		f = open(myfile,'r').read()
#		res = re.findall(r'"scan_id": "(\w.*)",',f)
#		if res:
		mhash = hashlib.md5(f).hexdigest()
#		fhash = spamsum.spamsum(f)
		#f.close()
		print "Iteration: ", count
		print "md5 Hash is: " + mhash
#		print "Fuzzy Hash is: " + fhash
#		f = open("/home/Dev/tillmann/dataset/labels.txt",'r')
#res = subprocess.Popen('grep "ff731f3c6a580ef165bdcf7aa08f1fff" labels.txt | gawk \'{print $2}\'', shell=True, stdout=subprocess.PIPE)
		reader = csv.reader(open("/home/fimz/Dev/datasets/tillmann/dataset/labels.txt", "r"), delimiter='\t')
		for rows in reader:
		     if mhash in rows:
			     print rows
			     print "Label = ", rows[1]
		             label = rows[1]

		logfile = label + "-" + mhash + ".binary"
		fp = open("./binary/" + logfile, 'w')
		fp.write( f )
		print "Written to file successfully"
#		fp.close()
#		f.close()
#		os.system("python get_streams.py "+ pathstr + "/" + infile )		
		count = count + 1

