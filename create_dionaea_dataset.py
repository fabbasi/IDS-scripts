##################################
# create_dionaea_dataset.py
#
# Description:
# Creates a dataset from dionaea bistreams.
# Copies streams and writes them out to the destination renaming them to their md5sum.
# Creates a list of the mapping between the md5sum and the original filename
# Usage:
# $ python create_dionaea_dataset.py ~/Dev/dionaea/bistreams ~/Dev/datasets/dionaea-streams
#
#
#
################################


#!/usr/bin/python

import sys, os, hashlib, errno, re, shutil

print "2 arguments required <source dionaea dataset dir> <target dataset directory/>"

source = sys.argv[1]
dest = sys.argv[2]

listing = os.listdir(source)

try:
	        os.makedirs(dest)
except os.error, e:
	        if e.errno != errno.EEXIST:
			        raise

mapf = open("/home/fimz/Dev/datasets/dionaea-mapping.txt",'w')
cache = []
for folder in listing:
   loc = source+"/"+folder	
   listofsamples = os.listdir(loc)
   for sample in listofsamples:
        if "http" not in sample:
		print "NON HTTP FLOW"
	stream = 0
	i = 0
	myfile = loc + "/" + sample
	print "Current file is: ", myfile
	try:
		os.remove("temp.py")
		os.remove("temp.pyc")
	except os.error, e:
		1
	os.system("cp " + myfile + " temp.py") ## create a temp py script by copying the sample
	f = open("temp.py",'r').read()
	if len(f) > 1:
		import temp	
		stream = temp.stream
		for i in stream:
		    print "Stream is:",stream
		    if stream not in cache:
			cache.append(stream)
			print "i:",i
			if i[0] == 'in':  ## attack
				print "in stream:"
				finalin = i[1]
		#		print finalin
				mhash = hashlib.md5(finalin).hexdigest()  ## create an md5sum of the source
				outf = open(dest+"/"+"X-"+mhash,'w') ## open output file for writting
				outf.write(finalin)	## Write to the newly renamed file
				mapf.write(sample + " " + mhash + "\n") ## append to the mapping file
				outf.close()
				finalin = 0

			if i[0] == 'out': ## response
				print "out stream:"
				finalout = i[1]
		#		print finalout
				mhash = hashlib.md5(finalout).hexdigest()  ## create an md5sum of the source
				outf = open(dest+"/"+"X-"+mhash,'w') ## open output file for writting
				outf.write(finalout)	## Write to the newly renamed file
				mapf.write(sample + " " + mhash + "\n") ## append to the mapping file
				outf.close()
				finalout = 0
		print "Length of cache: ", len(cache)
		del stream
		if "temp" in sys.modules:
		      del(sys.modules["temp"])

	#	print "Final stream:", stream

mapf.close()





