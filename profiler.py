#!/usr/bin/env python

###########################
# Script: Profiler
# Purpose: Parse Pcap files and create behavioral profiles from them. These profiles will contain
# the fields like [index, srcip, sport, dstip, dstport, prot, id, flags, payloadhash]. The Payload is hashed using
# fuzzy hashing technique defined in spamsum. Finally the output is written to a csv file for each packet
# 20110324: I have added support to only parse those TCP packets with TCP push flags. I have also added support to write hex values for src/dest ports and id.
#
# Author: Fahim Abbasi
# Date: 20100415
############################
import sys, csv, socket
#import dpkt
import spamsum
from scapy import *

#print sys.argv[1]

if len(sys.argv) < 3:
	print "Usage: ./profiler.py /path/to/pcap <iterationindex>"
	sys.exit

# = open(sys.argv[1])
pcapfile = sys.argv[1]
n = sys.argv[2]
print pcapfile
print n

from scapy.all import *
 
pcap = rdpcap(pcapfile) or die(error())
#n="1" 
dstport=""
sport=""
flags=""
prot=None

for pkt in pcap:

		 print n
		 print pkt[IP].src
##IP Header
		 try:	
			srcip= pkt[Ether][IP].src
			dstip= pkt[Ether][IP].dst
			prot= pkt[Ether][IP].proto
			id = pkt[Ether][IP].id
			id = hex(id)[2:]
#	                srcip = socket.inet_aton(srcip)
		 except IndexError:
		        srcip="0"
			dstip="0"
			prot="0"
			id="0"

	         if prot==6  :
##TCP Header
			 try:
				sport= pkt[Ether][IP][TCP].sport
				dstport= pkt[Ether][IP][TCP].dport
			 	flags= pkt.sprintf("%TCP.flags%")
				sport = hex(sport)[2:]
				dstport = hex(dstport)[2:]
			 except IndexError:
				sport="0"
				dstport="0"
				flags="0"
			 if "P" not in flags:
				continue

		 if prot==17 :
##UDP Header
			 try:
				sport= pkt[Ether][IP][UDP].sport
				dstport= pkt[Ether][IP][UDP].dport
				sport = hex(sport)[2:]
				dstport = hex(dstport)[2:]
# 	flags= pkt[Ether][IP][UDP].flags
			 except IndexError:
				sport="0"
				dstport="0"
#		sport="non"
#		dstport="non"
#	flags=""
		 else:
			 continue
			 try:
				sport= pkt[Ether][IP][TCP].sport
				dstport= pkt[Ether][IP][TCP].dport
		 		flags= pkt.sprintf("%TCP.flags%")
			 except IndexError:
				sport="0"
				dstport="0"
				flags="0"
 
##Raw Payload
		 try:
			rawpay = pkt[Raw].load
		 except IndexError:
			hashres="none"

		 if len(rawpay) > 0:
			hashres = spamsum.spamsum(rawpay)

# File name if TCP or UDP, currently on they are supported	
		 if prot==6 or prot==17 :
			    output=str(n)+"-"+srcip+"-"+str(prot)+"."+str(dstport)
		 else:
		     output=str(n)+"-"+srcip+"."+str(prot)
	         print "test" 
# Print Output
		 print output,"\t", srcip, sport," > ", dstip, dstport, prot, id, flags, hashres
		 file = open(output, "w")
		 cw = csv.writer(file)
		 cw.writerow([srcip,sport,dstip,dstport,prot,id,flags,hashres])
		 n=str(int(n)+1)
		 file.close()

#for ts, buf in pcap:
#	print ts,len(buf)
#    eth = dpkt.ethernet.Ethernet(buf)
#    ip = eth.data
#while protocol is tcp(6)
#    while (ip.p==6):
#    print ip.src 
   
#    print("TCP")
#	tcp = ip.data

#    if tcp.dport == 80 and len(tcp.data) > 0:
       # http = dpkt.http.Request(tcp.data)
#	print ip.src

#f.close()
