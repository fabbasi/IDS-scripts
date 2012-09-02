#######################################
# combined-ncdspam.py
# Functionality:
#
# 1. Use Cilibrasi and Vitanyi's Normalized Compression Distance
# to cluster a dataset of packet profiles.
# Author: Fahim Abbasi 20110316
# http://seat.massey.ac.nz/projects/honeynet
# Code based on wjt
# http://digitalhistoryhacks.blogspot.com
# 2. Calculate spamsum
# 3. Generate Graph
# 4. Generate UPGMA graph
# 5. Write combined spamsum + ncd score to file
#
# 20111205:
# Changed 'location' variable to be provided as command line parameter
# UPGMA file was redundant as the NCD output file is the same thing
# 20111220:
# Take 2 files as input and calculate NCD and spamsum scores and write
# the combined score to the result file
# 20120314:
# The combined score should be min(ncd,spsum)
# 20120318:
# Adding support to read model file and sig dir to create a list of signatures/exemplars
# 20120319:
# Move results to destination or output directory
# Removo list500.txt
# Usage:
# python get_scores.py --sigdir /home/fimz/Dev/datasets/balanced-raw/imbalanced-100 --datdir /home/fimz/Dev/datasets/testset --iter 1 --outdir /home/fimz/Dev/datasets/500-results/rev/profiles-raw --model mymodel.txt
######################################


#!/usr/bin/env python
import re, math, collections, sys , jellyfish
import os
import random
import zlib
import time
from decimal import *
import spamsum
import optparse

def tokenize( _str):
    stopwords = [',']
    tokens = collections.defaultdict(lambda: 0.)
    for m in re.finditer(r"(\w+)", _str, re.UNICODE):
#        m = m.group(1).lower()
 	m = m.group(1)
	if len(m) < 2: continue
        if m in stopwords: continue
        tokens[m] += 1

    return tokens
#end of tokenize


#pathstring = '/home/fimz/Dev/profiler/worm/exp-20110121-normal-n-worm/dataset/ncd'
def icr(filex, filey):
	xbytes = open(filex, 'r').read()
	ybytes = open(filey, 'r').read()
	cy = zlib.compress(ybytes,9)
	print "uncompressed: ",xbytes
	print "compressed: ",cy
	icr = len(cy)/float( len(xbytes) )
	print "ICR: ",icr
	return icr

# Select all packet profiles from the path directory provided
# For each unique pair, calculate NCD
#
#
##############################################
##############################################
## Main program starts here ##
##############################################
##############################################

oparser = optparse.OptionParser(usage="usage: %prog [options] filename")
oparser.add_option("-d","--datdir",
                   action="store",
                   dest = "datdir",
                   default = False,
                   help = "path to dataset directory")
oparser.add_option("-o","--outdir",
                   action="store",
                   dest = "outdir",
                   default = False,
                   help = "path to result output directory")

(options, args) = oparser.parse_args()


location = options.outdir ## output or result dir
#sigdir = options.sigdir  ## path to signature/exemplar dir
datdir = options.datdir  ## path to dataset dir
#iteration = options.itera ## iterations
#model = options.model  ## /path/to/model file
#square_matrix = options.square_matrix

#siglist = os.listdir(sigdir)
listing = os.listdir(datdir)
selection = []
#sigselect = []


for infile in listing:
#    print "current file is: " + infile
    selection.append( infile )

print len(selection), selection[0]
now = "%s"%int(time.time())

icrstr = "%s-icr-out.txt"%now

output = "output/"

os.system("mkdir output")
icrfile = open( output+icrstr,'w')

## Reduntant upgma file, ncd is sufficient
#upgmafile = open (output+upgmastr, 'w')

getcontext().prec = 4

for i in range(0, len(selection)):
#    print i
        fx = datdir + '/' + str(selection[i])
        fy = datdir + '/' + str(selection[i])
	icrscore = icr(fx,fy)		 
        icrfile.write(str(selection[i]) + " " + str(icrscore) + "\n")

icrfile.close()

print "Distances Successfully calculated and written out to files"

f = open("list500.txt",'w')

#location = "/home/fimz/Dev/datasets/500-results"
print "location: ",location
finalicr = location + "/" + icrstr
print "Final result file:",finalicr
f.write(finalicr  + "\n")

f.close()
f = open("result.file",'w')
f.write(finalicr)
f.close()
os.system("mv output/* "+location+"/") ## MOVE TO OUTPUT DIR
