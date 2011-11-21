#!/usr/bin/env python

###########################
# Script: Profiler
# Purpose: Parse Pcap files and create behavioral profiles from them. These profiles will contain
# the fields like [index, srcip, sport, dstip, dstport, prot, id, flags, hashresp]. The Payload is hashed using
# fuzzy hashing technique defined in spamsum. Finally the output is written to a csv file for each packet
#
# Author: Fahim Abbasi
# Date: 20100415
############################
import sys, csv
#import dpkt
import spamsum
from scapy import *

#print sys.argv[1]

if len(sys.argv) != 2:
	print "Usage: ./profiler.py /path/to/pcap"
	sys.exit

# = open(sys.argv[1])
pcapfile = sys.argv[1]

from scapy.all import *
 
pcap = rdpcap(pcapfile)
n="1" 
dstport=""
sport=""
flags=""
prot=None

for pkt in pcap:
##IP Header
		 try:	
			srcip= pkt[Ether][IP].src
			dstip= pkt[Ether][IP].dst
			prot= pkt[Ether][IP].proto
			id= pkt[Ether][IP].id
		 except IndexError:
		        srcip="none"
			dstip="none"
			prot=""
			id=""


	         if prot==6  :
##TCP Header
			 try:
				sport= pkt[Ether][IP][TCP].sport
				dstport= pkt[Ether][IP][TCP].dport
			 	flags= pkt.sprintf("%TCP.flags%")
			 except IndexError:
				sport="none"
				dstport="none"
				flags="none"
		 if prot==17 :
##UDP Header
			 try:
				sport= pkt[Ether][IP][UDP].sport
				dstport= pkt[Ether][IP][UDP].dport
# 	flags= pkt[Ether][IP][UDP].flags
			 except IndexError:
				sport=""
				dstport=""
#		sport="non"
#		dstport="non"
#	flags=""
		 else:
			 try:
				sport= pkt[Ether][IP][TCP].sport
				dstport= pkt[Ether][IP][TCP].dport
		 		flags= pkt.sprintf("%TCP.flags%")
			 except IndexError:
				sport="none"
				dstport="none"
				flags="none"
 
##Raw Payload
		 try:
			rawpay = pkt[Raw].load
		 except IndexError:
			hashres="none"

		 if len(rawpay) > 0:
			hashres = spamsum.spamsum(rawpay)
##Header Hash
			header = srcip+","+str(sport)+","+dstip+","+str(dstport)+","+str(prot)+","+str(id)+","+flags
			hhash = spamsum.spamsum( hhash )


# File name if TCP or UDP	
		 if prot==6 or prot==17 :
			    output=n+"-"+srcip+"-"+str(prot)+"."+str(dstport)
		 else:
		     output=n+"-"+srcip+"."+str(prot)
 
# Print Output
		 print output,"\t", srcip, sport," > ", dstip, dstport, prot, id, flags, hashres
		 file = open(output, "w")
		 cw = csv.writer(file)
		 cw.writerow([hhash,hashres])
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
