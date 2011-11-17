#######################################
# ncddist-with-graph-for-binary.py
# Functionality:
#
# Calculate similarity of binary files with NCD
# 1. Use Cilibrasi and Vitanyi's Normalized Compression Distance
# to cluster a dataset of packet profiles.
# Author: Fahim Abbasi 20111116
# http://seat.massey.ac.nz/projects/honeynet
# Code based on wjt
# http://digitalhistoryhacks.blogspot.com
# 5. Generate Graph
# 6. Generate UPGMA graph
######################################


#!/usr/bin/env python
import re, math, collections, sys , jellyfish
import os
import random
import zlib
import time
from decimal import *

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

def kldiv(_s, _t):
    if (len(_s) == 0):
        return 1e33

    if (len(_t) == 0):
        return 1e33

    ssum = 0. + sum(_s.values())
    slen = len(_s)

    tsum = 0. + sum(_t.values())
    tlen = len(_t)

    vocabdiff = set(_s.keys()).difference(set(_t.keys()))
    lenvocabdiff = len(vocabdiff)

    """ epsilon """
    epsilon = min(min(_s.values())/ssum, min(_t.values())/tsum) * 0.001

    """ gamma """
    gamma = 1 - lenvocabdiff * epsilon

    # print "_s: %s" % _s
    # print "_t: %s" % _t

    """ Check if distribution probabilities sum to 1"""
    sc = sum([v/ssum for v in _s.itervalues()])
    st = sum([v/tsum for v in _t.itervalues()])

    if sc < 9e-6:
        print "Sum P: %e, Sum Q: %e" % (sc, st)
        print "*** ERROR: sc does not sum up to 1. Bailing out .."
        sys.exit(2)
    if st < 9e-6:
        print "Sum P: %e, Sum Q: %e" % (sc, st)
        print "*** ERROR: st does not sum up to 1. Bailing out .."
        sys.exit(2)

    div = 0.
    for t, v in _s.iteritems():
        pts = v / ssum

        ptt = epsilon
        if t in _t:
            ptt = gamma * (_t[t] / tsum)

        ckl = (pts - ptt) * math.log(pts / ptt)

        div +=  ckl

    return div
#end of kldiv

#pathstring = '/home/fimz/Dev/profiler/worm/exp-20110121-normal-n-worm/dataset/ncd'

# Function to calculate the Levenshtein distance of the two files

def alldist(filex, filey):
    xread = open(filex, 'r').read()
    yread = open(filey, 'r').read()
    lvd = jellyfish.levenshtein_distance(xread,yread)
    dlvd= jellyfish.damerau_levenshtein_distance(xread,yread)

#    print lvd
    res = float( lvd / 100.00 )
    dres= float(dlvd / 100.00 )
#    print res
#print "Levenshtein Distance=",lv_d
#    jaro = jellyfish.jaro_distance(xread,yread)
## Added jaro-winkler distance by fahim 20111011
#    jarowink = jellyfish.jaro_winkler(xread,yread)
#    jaro = 1.0 - jaro
#    jarowink = 1.0 - jarowink
#	print "Jaro Distance = ",jaro
#    ham = jellyfish.hamming_distance(xread,yread)
#    ham = float ( ham / 100.00)
#	print "Hamming Distance = ", ham
#	print "KL-divergence between d1 and d2:", kldiv(tokenize(d1), tokenize(d2))
#	print "KL-divergence between d2 and d1:", kldiv(tokenize(d2), tokenize(d1))
#    kl = kldiv(tokenize(xread), tokenize(yread))

    return res, dres , jaro, jarowink, ham, kl

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

pathstring = sys.argv[1]
iteration = sys.argv[2]

listing = os.listdir(pathstring)
selection = []
for infile in listing:
    print "current file is: " + infile
    selection.append( infile )

print len(selection), selection[0]
now = "%s"%int(time.time())
ncdstr = "%s-ncd-out.txt"%now
#levstr = "%s-lev-out.txt"%now
#dlevstr = "%s-dlev-out.txt"%now
#jarostr = "%s-jaro-out.txt"%now
#jarowinkstr = "%s-jarowink-out.txt"%now
#hamstr = "%s-ham-out.txt"%now
upgmastr = "%s-upgma-out.txt"%now
output = "output/"

os.system("mkdir output")
ncdfile = open( output+ncdstr, 'w')
#levfile = open( output+levstr,'w')
#dlevfile = open( output+dlevstr,'w')
#jarofile = open( output+jarostr, 'w')
#jarowinkfile = open( output+jarowinkstr, 'w')
#hamfile = open( output+hamstr,'w')
upgmafile = open (output+upgmastr, 'w')

getcontext().prec = 4

for i in range(0, len(selection)):
#    print i
    for j in range(0, len(selection)):
        fx = pathstring + '/' + str(selection[i])
        fy = pathstring + '/' + str(selection[j])
        print fx, fy
        ncdfile.write(str(selection[i]) + " " + str(selection[j]) + " " + str(+Decimal(str(ncd(fx, fy)))) + "\n")
#        upgmafile.write("\'" + str(selection[i]) + "\'" + "," + "\'" + str(selection[j]) + "\'" + "," + str(ncd(fx, fy))+ "\n")
        upgmafile.write(str(selection[i]) + "," + str(selection[j]) + "," +  str(+Decimal(str(ncd(fx, fy)))) + "\n" )

#	lev, dlev, jaro, jarowink,  ham, kl = alldist(fx, fy)
#        levfile.write(str(selection[i]) + " " + str(selection[j]) + " " + str(+Decimal(str(lev))) + "\n")
#        dlevfile.write(str(selection[i]) + " " + str(selection[j]) + " " + str(+Decimal(str(lev))) + "\n")
#        jarofile.write(str(selection[i]) + " " + str(selection[j]) + " " + str(+Decimal(str(jaro))) + "\n")
#        jarowinkfile.write(str(selection[i]) + " " + str(selection[j]) + " " + str(+Decimal(str(jaro))) + "\n")
#        hamfile.write(str(selection[i]) + " " + str(selection[j]) + " " +  str(+Decimal(str(ham))) + "\n")
#        levfile.write(str(selection[i]) + " " + str(selection[j]) + " " + str(lev) + "\n")

ncdfile.close()
#levfile.close()
#dlevfile.close()
#jarofile.close()
#jarowinkfile.close()
#hamfile.close()
upgmafile.close()

print "Distances Successfully calculated and written out to files"
print "##########################################################"
print "Calculating graph"
os.system("python ncd-fimz-graph.py " +ncdstr)
#os.system("python ncd-fimz-graph.py " +levstr)
#os.system("python ncd-fimz-graph.py " +dlevstr)
#os.system("python ncd-fimz-graph.py " +jarostr)
#os.system("python ncd-fimz-graph.py " +jarowinkstr)
#os.system("python ncd-fimz-graph.py " +hamstr)


graphncd = "output/graph-" + ncdstr
#graphlev = "output/graph-" + levstr
#graphjaro = "output/graph-" + jarostr
#graphdlev = "output/graph-" + dlevstr
#graphjarowink = "output/graph-" + jarowinkstr
#graphham = "output/graph-" + hamstr

ncdpng = graphncd + ".svg"
#levpng = graphlev + ".svg"
#jaropng = graphjaro + ".svg"
#hampng = graphham + ".svg"
#dlevpng = graphdlev + ".svg"
#jarowinkpng = graphjarowink + ".svg"


print "Graph files Created"
print "##########################################################"
print "Running Neato on ncd"

os.system("sfdp -Tsvg "+ graphncd + " -o " + ncdpng)
os.system("sfdp -Tpng "+ graphncd + " -o " + ".png")

#print "Running Neato on lev"

#os.system("sfdp -Tsvg "+ graphlev + " -o " + levpng)

#print "Running Neato on jaro"

#os.system("sfdp -Tsvg "+ graphjaro + " -o " + jaropng)
#print "Running Neato on ham"

#os.system("sfdp -Tsvg "+ graphham + " -o " + hampng)

#print "Running Neato on dlev"

#os.system("sfdp -Tsvg "+ graphdlev + " -o " + dlevpng)

#print "Running Neato on jarowink"

#os.system("sfdp -Tsvg "+ graphjarowink + " -o " + jarowinkpng)

## Adding UPGMA support
print "Calculating UPGMA"

os.system("python upgma.py output/" + upgmastr)

## Removing list500.txt ##
#os.system("rm -f list500.txt")
## Append to output to create the list ##

f = open("list500.txt",'a')

location = "/home/fimz/Dev/datasets/500-results/binary"
#finalham = location + "/" + iteration + "/" + hamstr
#finallev =  location + "/" + iteration + "/" + levstr
#finaldlev =  location + "/" + iteration + "/" + dlevstr
#finaljaro =  location + "/" + iteration + "/" + jarostr
#finaljarowink = location + "/" + iteration + "/" + jarowinkstr
finalncd = location + "/" + iteration + "/" + ncdstr

#f.write(finalham  + "\n")
#f.write(finallev  + "\n")
#f.write(finaldlev + "\n")
#f.write(finaljaro  + "\n")
#f.write(finaljarowink  + "\n")
f.write(finalncd  + "\n")
f.close()
"""to -Tsvg ncd-dcb-graph.txt -o graph-ncd-dcb.pngto -Tsvg ncd-dcb-graph.txt -o graph-ncd-dcb.png
fp1 = open(a1,'r')
fp2 = open(a2,'r')

d1 = fp1.read()
d2 = fp2.read()


lv_d = jellyfish.levenshtein_distance(d1,d2)
print "Levenshtein Distance=",lv_d
jaro = jellyfish.jaro_distance(d1,d2)
print "Jaro Distance = ",jaro
ham = jellyfish.hamming_distance(d1,d2)
print "Hamming Distance = ", ham
print "KL-divergence between d1 and d2:", kldiv(tokenize(d1), tokenize(d2))
print "KL-divergence between d2 and d1:", kldiv(tokenize(d2), tokenize(d1))
"""
