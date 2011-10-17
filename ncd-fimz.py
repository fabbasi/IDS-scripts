# ncd-fimz.py
#
# Use Cilibrasi and Vitanyi's Normalized Compression Distance
# to cluster a dataset of packet profiles.
# Author: Fahim Abbasi 20110316
# http://seat.massey.ac.nz/projects/honeynet
#
# Code based on wjt
# http://digitalhistoryhacks.blogspot.com
#
# 26 jun 2007
import os
import bz2
import random
import zlib

pathstring = '/home/fimz/Dev/profiler/worm/exp-20110121-normal-n-worm/dataset/ncd'

# Function to calculate the NCD of two files based on zlib level 9 compression

def ncd(filex, filey):
    xbytes = open(filex, 'r').read()
    ybytes = open(filey, 'r').read()
    xybytes = xbytes + ybytes
    cx = zlib.compress(xbytes,9)
    cy = zlib.compress(ybytes,9)
    cxy = zlib.compress(xybytes)
    if len(cy) > len(cx):
        n = (len(cxy) - len(cx)) / float(len(cy))
    else:
        n = (len(cxy) - len(cy)) / float(len(cx))
    return n

# Select all packet profiles from the path directory provided
# For each unique pair, calculate NCD
#
#
listing = os.listdir(pathstring)
selection = []
for infile in listing:
    print "current file is: " + infile
    selection.append( infile )

print len(selection), selection[0]

outfile = open('ncd-dcb.txt', 'w')
for i in range(0, len(selection)):
    print i
    for j in range(0, len(selection)):
	fx = pathstring + '/' + str(selection[i])
	fy = pathstring + '/' + str(selection[j])
	print fx, fy
	outfile.write(str(selection[i]) + " " + str(selection[j]) + " " + str(ncd(fx, fy)) + "\n")

outfile.close()
    
