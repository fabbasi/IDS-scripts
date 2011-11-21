# pynids Example
# $Id: Example,v 1.3 2005/01/27 04:53:45 mjp Exp $
# 
# Description: Get TCP/UDP and IP streams from pcaps and write them to output file with timestamp and details in the file label.
#


import os, pwd
import sys
import nids
import struct
import time
import spamsum
import re

logdir = "./output"
NOTROOT = "nobody"   # edit to taste
end_states = (nids.NIDS_CLOSE, nids.NIDS_TIMEOUT, nids.NIDS_RESET)

def handleTcpStream(tcp):
    print "tcps -", str(tcp.addr), " state:", tcp.nids_state
    if tcp.nids_state == nids.NIDS_JUST_EST:
        # new to us, but do we care?
        ((src, sport), (dst, dport)) = tcp.addr
	print tcp.addr
#        if dport in (80, 8000, 8080):
        print "collecting..."
        tcp.client.collect = 1
        tcp.server.collect = 1
    elif tcp.nids_state == nids.NIDS_DATA:
        # keep all of the stream's new data
    	tcp.discard(0)
    elif tcp.nids_state in end_states:
#	fpserver = open("/home/fimz/server.out",'w')
#	fpclient = open("/home/fimz/client.out",'w')
        print "addr:", tcp.addr
        print "To server:"
#        print tcp.server.data # WARNING - may be binary
#	logTcp(tcp)
#	print "After: "
 #       print tcp.server.data # WARNING - may be binary

#	fpserver.write(tcp.server.data[:tcp.server.count])
        print "To client:"
#        print tcp.client.data # WARNING - as above
#	fpclient.write(tcp.client.data[:tcp.client.count])
	logTcp(tcp)

def long2ip(val):
    # convert long IP addresses to dotted quad notation
    slist = []
    for x in range(0,4):
        slist.append(str(int(val >> (24 - (x * 8)) & 0xFF))) 
    return ".".join(slist)

def logTcp(tcp):
    tfilename = nids.param('filename')
    print tfilename
    pattern = re.compile(r'\/\w*.pcap')
    test = re.findall(pattern, tfilename)
    mystr = str(test).strip('[]\'/')
    temp = mystr.split(".")
    filename = temp[0]
    srcip = tcp.addr[0][0]
    srcport = tcp.addr[0][1]
    dstip = tcp.addr[1][0]
    dstport = tcp.addr[1][1]
    # client to server
    fname = "%s/%s-%s-%s-%s-%s-%s-CtoS.tcp" % (logdir, filename, int(time.time()), 
	     tcp.addr[0][0], tcp.addr[0][1], tcp.addr[1][0], tcp.addr[1][1])
    try: f = open(fname, "w")
    except: 
        print "unable to log to", logdir
        return
    toserver = tcp.server.data[:tcp.server.count]
    f.write(toserver)
    f.close()
    print "Client to Server: "+fname
    fname = "%s/%s-%s-%s-%s-%s-%s-CtoS-tcp.fuzz" % (logdir, filename, int(time.time()), 
	     srcip, srcport, dstip, dstport)
    try: g = open(fname, "w")
    except: 
        print "unable to log to", logdir
        return
    g.write(spamsum.spamsum(toserver))
    g.close()
    print "Client to Server Hashed :"+fname
    srcip = tcp.addr[0][0]
    srcport = tcp.addr[0][1]
    dstip = tcp.addr[1][0]
    dstport = tcp.addr[1][1]
    # server to client
    fname = "%s/%s-%s-%s-%s-%s-%s-StoC.tcp" % (logdir, filename, int(time.time()), 
 	     tcp.addr[1][0], tcp.addr[1][1], tcp.addr[0][0], tcp.addr[0][1])
    f = open(fname, "w")
    toclient = tcp.client.data[:tcp.client.count]
    f.write(toclient)
    f.close()
    print "Server to Client: "+fname
    fname = "%s/%s-%s-%s-%s-%s-%s-StoC-tcp.fuzz" % (logdir, filename, int(time.time()), 
	      dstip, dstport, srcip, srcport)
    try: g = open(fname, "w")
    except: 
        print "unable to log to", logdir
        return
    g.write(spamsum.spamsum(toclient))
    g.close()
    print "Sever to Client Hashed: "+fname


def logPkt(addr, payload, proto=17):
    tfilename = nids.param('filename')
    print tfilename
    pattern = re.compile(r'\/\w*.pcap')
    test = re.findall(pattern, tfilename)
    mystr = str(test).strip('[]\'/')
    temp = mystr.split(".")
    filename = temp[0]
   # log a single packet, for UDP and other IP (non-TCP)
    ip_p = {'proto1':'icmp', 'proto2':'igmp', 6:'tcp', 17:'udp', 41:'ipv6', 47:'gre', 
            50:'esp', 51:'ah', 58:'icmp6', 94:'ipip', 115:'l2tp', 255:'raw'}
    if proto == 17:
        fname = "%s/%s-%s-%s-%s-%s-%s.udp" % (logdir, filename, int(time.time()), 
		 addr[0][0], addr[0][1], addr[1][0], addr[1][1])
    else:
	proto = ip_p.get(proto, proto)
	print proto
#	pktproto = ip_p[proto]
        fname = "%s/%s-%s-%s-%s.%s" % (logdir, filename, int(time.time()), 
		 long2ip(addr[0]), long2ip(addr[1]), proto)
    f = open(fname, "w")
    f.write(payload)
    f.close()
    print fname
    fname = fname + ".fuzz"
    try: g = open(fname, "w")
    except: 
        print "unable to log to", logdir
        return
    g.write(spamsum.spamsum(payload))
    g.close()
    print fname


def handleUDP(addr, payload, pkt):
    # format of addr: 
    ((src, sport), (dst, dport)) = addr
    logPkt(addr, payload)
#    logPkt(addr, payload)

def handleIp(pkt):
    # handle an IP packet here ... dpkt, perhaps?
    v_hl, tos, len, id, off, ttl, p, sum, src, dst = \
	struct.unpack("!BBHHHBBHII", pkt[0:20])
    if p & 0xff == 6 or p & 0xff == 17:
        return					# ignore
    try: 
        if len(pkt) < 20: return
    except: pass
    proto = "proto%d" % (int(p) & 0xff)
    addr = (src, dst)

    # do the search 
#    match = 0
    payload = pkt[20:]				# XXX, ignores v_hl
#    logPkt(addr, payload, proto)
    logPkt(addr, payload, proto)

	

def main():

    #nids.param("pcap_filter", "tcp")       # bpf restrict to TCP only, note
                                            # libnids caution about fragments

    nids.param("scan_num_hosts", 0)         # disable portscan detection

    nids.chksum_ctl([('0.0.0.0/0', False)]) # disable checksumming

    if len(sys.argv) == 2:                  # read a pcap file?
        nids.param("filename", sys.argv[1])

    nids.init()

    nids.register_tcp(handleTcpStream)
    nids.register_udp(handleUDP)
    nids.register_ip(handleIp)

    print "pid", os.getpid()

    # Loop forever (network device), or until EOF (pcap file)
    # Note that an exception in the callback will break the loop!
    try:
        nids.run()
    except nids.error, e:
        print "nids/pcap error:", e
    except Exception, e:
        print "misc. exception (runtime error in user callback?):", e

if __name__ == '__main__':
    main()
