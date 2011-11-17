#####################
#
# Description: For a given file that contains a list of target files, this  script will read and submit the file to VT for a scan. Resulting scan identifier is written to an output file with timestamp
###################

import postfile
import sys
import time

inputfile = sys.argv[1]
flist = list()
f = open(inputfile,"r")
for line in f.xreadlines():
	line = line.strip('\n')
	flist.append(line)
	print line

host = "www.virustotal.com"
selector = "http://www.virustotal.com/api/scan_file.json"
fields = [("key", "aecd6ad458de6f01d48c8c544c2f12b96a7573b3c7c26875b276d4d1e28b6871")]
count = 1
for myfile in flist:
	print "Count = %d"%count
	if count % 19 != 0:
		print "Sending file: " + myfile
		file_to_send = open("./output/" + myfile, "rb").read()
		files = [("file", "./output/" + myfile , file_to_send)]
		json = postfile.post_multipart(host, selector, fields, files)
		print "File Submitted Successfully"
		print "json: " + json
		filestring = "./report/"+str(int(time.time()))+"-"+str(myfile)+".report"
		fname = open(filestring,'w')
		fname.write(json)
		print "Report Written to file : " + filestring
		count = count + 1
	else:
		print "Taking a 5 minute nap"
		count = count + 1
		time.sleep(300)
