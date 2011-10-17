import re
import csv
import sys
import time

#history
#cache
labels = list()
labellist = list()
badlist = list()
history = list()
#reader = csv.reader( open("1305675944-ncd-out.txt",'r'), delimiter = ' ')
#for line in reader:
#	history = line[0]
#	break
#float thres
#thres = sys.argv[1]

def lookupbad(value):
	a = value[0]
	b = value[1]
	s = value[2]
	label = a+","+b+","+s
	if not badlist:
		badlist.append(label)
#	for labels in badlist:
	if label in badlist:
		1
	else:
		badlist.append(label)

#	print labellist
	return badlist


def lookuplist(label):
	if not labellist:
		labellist.append(label)
#	for labels in labellist:
	if label in labellist:
		1
	else:
		labellist.append(label)
	return labellist

def historylist(line):
### Reduced the sample space to search by not accounting for previously seen labels ###
	status = 0
	x = line[0]
	y = line[1]
	xy = x + "," + y
	yx = y + "," + x
	label = xy
	print len(history)
#	if not history:
#		history.append(xy)
#		history.append(yx)
#	print len(history)
#	for labels in history:
#	print len(history)
#	print labels
	print "History size:%s" % sys.getsizeof(history)
	if label in history:
		print "Label Found"
		status = 0
		return 0 
#		break
	else:
		print "Labels not found adding them now"
		if xy == yx:
			history.append(xy)
		else:
			history.append(xy)
			history.append(yx)
		status = 1
		return 1
#			break
	return status

print "File name to parse required as a single argument to this script"
infile = sys.argv[1]

output = "%s-66-result.txt"%int(time.time())
f = open(output,'w')
f.write("Labels\n Threshold, 100, 300, 600, 700, 800, 900, sum of good, size of good labels , inc 100, inc 300, inc 600, inc 700, inc 800, inc 900, Incorrect label combinations,  Incorrect, totalFN, FN100, FN300, FN600, FN700, FN800, FN900, Normalized TP, Normalized FP \n")
f.close()

thres = 0.95
while(float(thres) > 0):
	count300 = 0
	count10 = 0
	count100 = 0
	count600 = 0
	count700 = 0
	count900 = 0
	count800 = 0
	fncount300 = 0
	fncount10 = 0
	fncount100 = 0
	fncount600 = 0
	fncount700 = 0
	fncount900 = 0
	fncount800 = 0

	inc = 0
	inc100 = 0
	inc300 = 0
	inc600 = 0
	inc700 = 0
	inc800 = 0
	inc900 = 0
	no100 = 0
	incorrect = 0
	newlabel = 0
	totalfn = 0
	badlabel100 = []
	badlabel300 = []
	badlabel600 = []
	badlabel700 = []
	badlabel800 = []
	badlabel900 = []
#	reader = csv.reader( open("/home/fimz/Dev/disk-2/datasets/66-dataset/1306809242-ncd-out.txt",'r'), delimiter = ' ')
	reader = csv.reader( open(infile,'r'), delimiter = ' ')

	for line in reader:
		print line
#		newlabel = historylist(line)
#		print "Newlabel=", newlabel
#		if newlabel == 1:
#		print "True"
		cache = line[0]
		val = line[2]
		if float(val) > float(thres):
			print "Below Threshold"
			if re.match(r'^1\d{2}-*',line[0]):
				if re.match(r'^1[0-9]{2}-*', line[1]):
					count100 = count100 + 1				
					print "100:",line
					no100 = 0
					lookuplist(str(line[0]))
				else: 
					no100 = 1
					inc100 = inc100 + 1
					badlabel100.append(line[1])
			else: no100 = 1
			if re.match(r'3[0-9][0-9]-*',line[0]):
				if re.match(r'3[0-9][0-9]-*',line[1]):
					count300 = count300 + 1				
					print "300:",line
					lookuplist(str(line[0]))
					no300 = 0
				else: 
					no300 = 1
					inc300 = inc300 + 1
					badlabel300.append(line[1])
			else: no300 = 1
			if re.match(r'6[0-9][0-9]-*',line[0]):
				if re.match(r'6[0-9][0-9]-*',line[1]):
					count600 = count600 + 1				
					print "600:",line
					no600 = 0
					lookuplist(str(line[0]))
				else: 
					no600 = 1
					inc600 = inc600 + 1
					badlabel600.append(line[1])
			else: no600 = 1
			if re.match(r'7[0-9][0-9]-*',line[0]):
				if re.match(r'7[0-9][0-9]-*',line[1]):
					count700 = count700 + 1				
					print "700:",line
					no700 = 0
					lookuplist(str(line[0]))
				else: 
					no700 = 1
					inc700 = inc700 + 1
					badlabel700.append(line[1])
			else: no700 = 1
			if re.match(r'9[0-9][0-9]-*',line[0]):
				if re.match(r'9[0-9][0-9]-*',line[1]):
					count900 = count900 + 1				
					print "900:",line
					no900 = 0
					lookuplist(str(line[0]))
				else:
					no900 = 1
					inc900 = inc900 + 1
					badlabel900.append(line[1])
			else: no900 = 1
			if re.match(r'8[0-9]{2}-*',line[0]):
				if re.match(r'8[0-9]{2}-*',line[1]):
					count800 = count800 + 1				
					print "800:",line
					no800 = 0
					lookuplist(str(line[0]))
				else: 
					no800 = 1
					inc800 = inc800 + 1
					badlabel800.append(line[1])
			else: no800 = 1
			if no800 == 1 and no900 == 1 and no700 == 1 and no600 == 1 and no300 == 1 and no100 == 1:
				inc = inc + 1
				lookupbad(line)		
			incorrect = inc100 + inc300 + inc600 + inc700 + inc800 + inc900
		else:
			print "Above threshold"
			if re.match(r'^1\d{2}-*',line[0]):
				if re.match(r'^1[0-9]{2}-*', line[1]):
					fncount100 = fncount100 + 1				
					print "100:",line
#						no100 = 0
#						lookuplist(str(line[0]))
#				else: no100 = 1
			if re.match(r'3[0-9][0-9]-*',line[0]):
				if re.match(r'3[0-9][0-9]-*',line[1]):
					fncount300 = fncount300 + 1				
					print "300:",line
#						lookuplist(str(line[0]))
#						no300 = 0
#				else: no300 = 1
			if re.match(r'6[0-9][0-9]-*',line[0]):
				if re.match(r'6[0-9][0-9]-*',line[1]):
					fncount600 = fncount600 + 1				
					print "600:",line
#						no600 = 0
#						lookuplist(str(line[0]))
			if re.match(r'7[0-9][0-9]-*',line[0]):
				if re.match(r'7[0-9][0-9]-*',line[1]):
					fncount700 = fncount700 + 1				
					print "700:",line
#						no700 = 0
#						lookuplist(str(line[0]))
			if re.match(r'9[0-9][0-9]-*',line[0]):
				if re.match(r'9[0-9][0-9]-*',line[1]):
					fncount900 = fncount900 + 1				
					print "900:",line
			if re.match(r'8[0-9]{2}-*',line[0]):
				if re.match(r'8[0-9]{2}-*',line[1]):
					fncount800 = fncount800 + 1				
					print "800:",line

			totalfn = fncount100 + fncount300 + fncount600 + fncount700 + fncount800 + fncount900
			print "total FN =%s" % totalfn

#	else:
#		continue

		#			print line	
	print "Labels =\n 100 = %s,\n 300 = %s,\n 600 = %s,\n 700 = %s,\n 900 = %s,\n 800 = %s\n" % (count100, count300, count600, count700, count900, count800)
	print "Incorrect labels = %s" % inc
	labellist = lookuplist(line[0])
	print labellist
	print "size good:",len(labellist)
	bad = lookupbad(line)
	print "Bad:\n", bad
	print "size bad:", len(bad)
	print "When Threshold: %s, Incorrect: %s"%(thres,inc)
	sumofgood = count100 + count300 + count600 + count700 + count800 + count900
	normtp = sumofgood/1074.
	normfp = incorrect/3282.
	f = open(output,'a')
#	f.write("Labels\n Threshold, 100, 300, 600, 700, 800, 900, sum of good, size of good labels , inc 100, inc 300, inc 600, inc 700, inc 800, inc 900, Incorrect label combinations,  Incorrect, totalFN, FN100, FN300, FN600, FN700, FN800, FN900, inc100label, inc300label, inc600label, inc700label, inc800label, inc900label \n")
#	f.write(("%s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s , %s, %s , %s ,%s ,%s ,%s ,%s ,%s ,%s , %s, %s ,%s ,%s ,%s ,%s ,%s ,%s \n") % ( thres, count100, count300, count600, count700, count800, count900, sumofgood, len(labellist) , inc100, inc300, inc600, inc700, inc800, inc900, inc, len(bad), totalfn , fncount100, fncount300, fncount600, fncount700, fncount800, fncount900, ' ; '.join(badlabel100), ' ; '.join(badlabel300), ' ; '.join(badlabel600), ' ; '.join(badlabel700), ' ; '.join(badlabel800), ' ; '.join(badlabel900) ))
	f.write(("%s, %s, %s, %s,%s,%s,%s,%s,%s , %s, %s , %s ,%s ,%s ,%s ,%s ,%s ,%s , %s, %s ,%s ,%s ,%s ,%s ,%s ,%s \n") % ( thres, count100, count300, count600, count700, count800, count900, sumofgood, len(labellist) , inc100, inc300, inc600, inc700, inc800, inc900, inc, incorrect, totalfn , fncount100, fncount300, fncount600, fncount700, fncount800, fncount900, normtp , normfp ))

#	f.write("Incorrect per class\n")
#	f.write(("%s,%s,%s,%s,%s,%s\n") % (inc100, inc300, inc600, inc700, inc900, inc800))
#	f.write("Incorrect label combinations = %s\n" % inc)
#	f.write("size good: %s\n"%len(labellist))
#	f.write( "Bad: %s\n"% bad)
#	f.write("size bad: %s\n"% len(bad))
#	f.write("When Threshold: %s, Incorrect: %s\n"%(thres,inc))
	f.close()
	history = []
	thres = thres - 0.05

