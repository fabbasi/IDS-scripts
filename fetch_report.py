#!/usr/bin/env python

###################################
# Author: Fahim Abbasi
# Date: 20110510
# Description: The fetch_report script, lists all report files in the report folder, parses the report id from them and posts the id off to VT for a scan report request. The result is then written to an output file with timestamp
#
###################################



import simplejson
import urllib
import urllib2
import sys
import os
import time
from urllib2 import HTTPError, URLError
from urllib2 import *
import re

#hash = sys.argv[1]

reportdir = "./report"

logfile = "%s-vt-malware-results.txt"% int(time.time())
fp = open(logfile,"w")
inc = 0
#while "0" in pathstr:

listing = os.listdir(reportdir)
selection = [] 
count = 1
print "List length= ", len(listing)
for infile in listing:
	if count%19 == 0:
		print "Taking a 5 min nap....zzzzz..."
		time.sleep(300)	
		count = count + 1
	else:
		print "Current file is: ./report/" + infile
#		print "File Submitted Successfully"
	#temphash = infile.split(".")	
		myfile = "./report/" + infile
	#	fhash = temphash[0]
		f = open(myfile,'r').read()
		res = re.findall(r'"scan_id": "(\w.*)",',f)
		fhash = res[0]
		print "Hash is: " + fhash
		url = "https://www.virustotal.com/api/get_file_report.json"
		parameters = {"resource": fhash,
			       "key": "aecd6ad458de6f01d48c8c544c2f12b96a7573b3c7c26875b276d4d1e28b6871"}
		data = urllib.urlencode(parameters)
		req = urllib2.Request(url, data)
		try:
		    response = urllib2.urlopen(req)
		except HTTPError, e:
		    print 'The server couldn\'t fulfill the request.'
		    print 'Error code: ', e.code
		except URLError, e:
		    print 'We failed to reach a server.'
		    print 'Reason: ', e.reason
		json = response.read()
		print json
		fp.write(infile + ", " + fhash + ", " + json + "\n")
		print "Written to file successfully"
#		os.system("python get_streams.py "+ pathstr + "/" + infile )		
		count = count + 1
