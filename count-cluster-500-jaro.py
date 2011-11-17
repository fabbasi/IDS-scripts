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
output = "%s-500-result.txt"%int(time.time())
f = open(output,'w')
f.write("Labels\n Threshold, 10, 11, 13, 131, 132, 133, 134, 135, 14, 1411, 1412, 145, 146, 12, 18, sum of good, size of good labels , inc 10, inc 11, inc13 , inc 131, inc 132, inc 133, inc 134, inc 135, inc 14, inc 1411, inc 1412, inc 145, inc 146, inc 12, inc 18, Incorrect label combinations,  Incorrect, totalFN, FN10, FN11, FN13, FN131, FN132, FN133, FN 134, FN135, FN14, FN1411, FN1412, FN145, FN146, FN12, FN18, Normalized TP, Normalized FP \n")
f.close()

## Read input file from command line
infile = sys.argv[1]

thres = 0.95
while(float(thres) > 0):
	count1411 = 0
	count1412 = 0
	count145 = 0
	count146 = 0
	count12 = 0
	count18 = 0
	count12 = 0
	count10 = 0
	count11 = 0
	count13 = 0
	count131 = 0
	count132 = 0
	count133 = 0
	count134 = 0
	count135 = 0
	count14 = 0

	fncount14 = 0
	fncount1412 = 0
	fncount10 = 0
	fncount1411 = 0
	fncount145 = 0
	fncount146 = 0
	fncount18 = 0
	fncount12 = 0
	fncount10 = 0
	fncount11 = 0
	fncount13 = 0
	fncount131 = 0
	fncount132 = 0
	fncount133 = 0
	fncount134 = 0
	fncount135 = 0

	inc = 0
	inc1411 = 0
	inc1412 = 0
	inc145 = 0
	inc146 = 0
	inc12 = 0
	inc18 = 0
	inc10 = 0
	inc11 = 0
	inc13 = 0
	inc131 = 0
	inc132 = 0
	inc133 = 0
	inc134 = 0
	inc135 = 0
	inc14 = 0
	
	no14 = 0
	no1411 = 0
	incorrect = 0
	newlabel = 0
	totalfn = 0
	badlabel1411 = []
	badlabel1412 = []
	badlabel145 = []
	badlabel146 = []
	badlabel12 = []
	badlabel18 = []
	badlabel10 = []
	badlabel11 = []
	badlabel12 = []
	badlabel13 = []
	badlabel131 = []
	badlabel132 = []
	badlabel133 = []
	badlabel134 = []
	badlabel135 = []
	badlabel14 = []

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
			if re.match(r'^10-.*.fuzz',line[0]):
				if re.match(r'^10-.*.fuzz', line[1]):
					count10 = count10 + 1				
					print "10:",line
					no10 = 0
					lookuplist(str(line[0]))
				else: 
					no10 = 1
					inc10 = inc10 + 1
					badlabel10.append(line[1])
			else: no10 = 1
			if re.match(r'11-.*.fuzz',line[0]):
				if re.match(r'11-.*.fuzz',line[1]):
					count11 = count11 + 1				
					print "11:",line
					lookuplist(str(line[0]))
					no11 = 0
				else: 
					no11 = 1
					inc11 = inc11 + 1
					badlabel11.append(line[1])
			else: no11 = 1
			if re.match(r'13.[1-9]*-.*.fuzz',line[0]):
				if re.match(r'13.[1-9]*-.*.fuzz',line[1]):
					count13 = count13 + 1				
					print "13:",line
					no13 = 0
					lookuplist(str(line[0]))
				else: 
					no13 = 1
					inc13 = inc13 + 1
					badlabel13.append(line[1])
			else: no13 = 1
			if re.match(r'13.1-.*.fuzz',line[0]):
				if re.match(r'13.1-.*.fuzz',line[1]):
					count131 = count131 + 1				
					print "131:",line
					no131 = 0
					lookuplist(str(line[0]))
				else: 
					no131 = 1
					inc131 = inc131 + 1
					badlabel131.append(line[1])
			else: no131 = 1
			if re.match(r'13.2-.*.fuzz',line[0]):
				if re.match(r'13.2-.*.fuzz',line[1]):
					count132 = count132 + 1				
					print "132:",line
					no132 = 0
					lookuplist(str(line[0]))
				else:
					no132 = 1
					inc132 = inc132 + 1
					badlabel132.append(line[1])
			else: no132 = 1
			if re.match(r'13.3-.*.fuzz',line[0]):
				if re.match(r'13.3-.*.fuzz',line[1]):
					count133 = count133 + 1				
					print "133:",line
					no133 = 0
					lookuplist(str(line[0]))
				else: 
					no133 = 1
					inc133 = inc133 + 1
					badlabel133.append(line[1])
			else: no133 = 1
			if re.match(r'13.4-.*.fuzz',line[0]):
				if re.match(r'13.4-.*.fuzz',line[1]):
					count134 = count134 + 1				
					print "134:",line
					no134 = 0
					lookuplist(str(line[0]))
				else:
					no134 = 1
					inc134 = inc134 + 1
					badlabel134.append(line[1])
			else: no134 = 1
			if re.match(r'13.5-.*.fuzz',line[0]):
				if re.match(r'13.5-.*.fuzz',line[1]):
					count135 = count135 + 1				
					print "135:",line
					no135 = 0
					lookuplist(str(line[0]))
				else: 
					no135 = 1
					inc135 = inc135 + 1
					badlabel135.append(line[1])
			else: no135 = 1
			if re.match(r'^14.1.1-.*.fuzz',line[0]):
				if re.match(r'^14.1.1-.*.fuzz', line[1]):
					count1411 = count1411 + 1				
					print "14.1.1:",line
					no1411 = 0
					lookuplist(str(line[0]))
				else: 
					no1411 = 1
					inc1411 = inc1411 + 1
					badlabel1411.append(line[1])
			else: no1411 = 1
			if re.match(r'14.[1-9]+[.]?[1-9]?-.*.fuzz',line[0]):
				if re.match(r'14.[1-9]+[.]?[1-9]?-.*.fuzz',line[1]):
					count14 = count14 + 1				
					print "14:",line
					no14 = 0
					lookuplist(str(line[0]))
				else: 
					no14 = 1
					inc14 = inc14 + 1
					badlabel14.append(line[1])
			else: no13 = 1
			if re.match(r'14.1.2-.*.fuzz',line[0]):
				if re.match(r'14.1.2-.*.fuzz',line[1]):
					count1412 = count1412 + 1				
					print "1412:",line
					lookuplist(str(line[0]))
					no1412 = 0
				else: 
					no1412 = 1
					inc1412 = inc1412 + 1
					badlabel1412.append(line[1])
			else: no1412 = 1
			if re.match(r'14.5-.*.fuzz',line[0]):
				if re.match(r'14.5-.*.fuzz',line[1]):
					count145 = count145 + 1				
					print "145:",line
					no145 = 0
					lookuplist(str(line[0]))
				else: 
					no145 = 1
					inc145 = inc145 + 1
					badlabel145.append(line[1])
			else: no145 = 1
			if re.match(r'14.6-.*.fuzz',line[0]):
				if re.match(r'14.6-.*.fuzz',line[1]):
					count146 = count146 + 1				
					print "146:",line
					no146 = 0
					lookuplist(str(line[0]))
				else: 
					no146 = 1
					inc146 = inc146 + 1
					badlabel146.append(line[1])
			else: no146 = 1
			if re.match(r'18-.*.fuzz',line[0]):
				if re.match(r'18-.*.fuzz',line[1]):
					count18 = count18 + 1				
					print "18:",line
					no18 = 0
					lookuplist(str(line[0]))
				else:
					no18 = 1
					inc18 = inc18 + 1
					badlabel18.append(line[1])
			else: no18 = 1
			if re.match(r'12-.*.fuzz',line[0]):
				if re.match(r'12-.*.fuzz',line[1]):
					count12 = count12 + 1				
					print "12:",line
					no12 = 0
					lookuplist(str(line[0]))
				else: 
					no12 = 1
					inc12 = inc12 + 1
					badlabel12.append(line[1])
			else: no12 = 1
 			if no12 == 1 and no18 == 1 and no146 == 1 and no145 == 1 and no1412 == 1 and no1411 == 1 and no10 ==1 and no11 == 1 and no13 ==1 and no131 ==1 and no132 == 1 and no133 == 1 and no134 == 1 and no135 == 1 and no14:
				inc = inc + 1
				lookupbad(line)		
			incorrect = inc1411 + inc1412 + inc145 + inc146 + inc12 + inc18 + inc10 + inc11 + inc13 + inc131 + inc132 + inc133 + inc134 + inc135 + inc14
		else:
			print "Above threshold"
			if re.match(r'^14.1.1-*.fuzz',line[0]):
				if re.match(r'^14.1.1-*.fuzz', line[1]):
					fncount1411 = fncount1411 + 1				
					print "1411:",line
#						no1411 = 0
#						lookuplist(str(line[0]))
#				else: no1411 = 1
			if re.match(r'14.1.2-*.fuzz',line[0]):
				if re.match(r'14.1.2-*.fuzz',line[1]):
					fncount1412 = fncount1412 + 1				
					print "1412:",line
#						lookuplist(str(line[0]))
#						no1412 = 0
#				else: no1412 = 1
			if re.match(r'14.5-*.fuzz',line[0]):
				if re.match(r'14.5-*.fuzz',line[1]):
					fncount145 = fncount145 + 1				
					print "145:",line
#						no145 = 0
#						lookuplist(str(line[0]))
			if re.match(r'14.6-*.fuzz',line[0]):
				if re.match(r'14.6-*.fuzz',line[1]):
					fncount146 = fncount146 + 1				
					print "146:",line
#						no146 = 0
#						lookuplist(str(line[0]))
			if re.match(r'18-*.fuzz',line[0]):
				if re.match(r'18-*.fuzz',line[1]):
					fncount18 = fncount18 + 1				
					print "18:",line
			if re.match(r'12-*.fuzz',line[0]):
				if re.match(r'12-*.fuzz',line[1]):
					fncount12 = fncount12 + 1				
					print "12:",line

			totalfn = fncount1411 + fncount1412 + fncount145 + fncount146 + fncount12 + fncount18
			print "total FN =%s" % totalfn

#	else:
#		continue

		#			print line	
	print "Labels =\n 1411 = %s,\n 1412 = %s,\n 145 = %s,\n 146 = %s,\n 18 = %s,\n 12 = %s\n" % (count1411, count1412, count145, count146, count18, count12)
	print "Incorrect labels = %s" % inc
	labellist = lookuplist(line[0])
	print labellist
	print "size good:",len(labellist)
	bad = lookupbad(line)
	print "Bad:\n", bad
	print "size bad:", len(bad)
	print "When Threshold: %s, Incorrect: %s"%(thres,inc)
	sumofgood = count13 + count14 + count12 + count18 + count10
	normtp = sumofgood/1074.
	normfp = incorrect/3282.
	f = open(output,'a')
#	f.write("Labels\n Threshold, 1411, 1412, 145, 146, 12, 18, sum of good, size of good labels , inc 1411, inc 1412, inc 145, inc 146, inc 12, inc 18, Incorrect label combinations,  Incorrect, totalFN, FN1411, FN1412, FN145, FN146, FN12, FN18, inc1411label, inc1412label, inc145label, inc146label, inc12label, inc18label \n")
#	f.write(("%s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s , %s, %s , %s ,%s ,%s ,%s ,%s ,%s ,%s , %s, %s ,%s ,%s ,%s ,%s ,%s ,%s \n") % ( thres, count1411, count1412, count145, count146, count12, count18, sumofgood, len(labellist) , inc1411, inc1412, inc145, inc146, inc12, inc18, inc, len(bad), totalfn , fncount1411, fncount1412, fncount145, fncount146, fncount12, fncount18, ' ; '.join(badlabel1411), ' ; '.join(badlabel1412), ' ; '.join(badlabel145), ' ; '.join(badlabel146), ' ; '.join(badlabel12), ' ; '.join(badlabel18) ))
#f.write("Labels\n Threshold, 10, 11, 13, 131, 132, 133, 134, 135, 1411, 1412, 145, 146, 12, 18, sum of good, size of good labels , inc 10, inc 11, inc13 , inc 131, inc 132, inc 133, inc 134, inc 135, inc 1411, inc 1412, inc 145, inc 146, inc 12, inc 18, Incorrect label combinations,  Incorrect, totalFN, FN10, FN11, FN13, FN131, FN132, FN133, FN 134, FN135, FN1411, FN1412, FN145, FN146, FN12, FN18, Normalized TP, Normalized FP \n")

	f.write(("%s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s, %s, %s, %s,%s,%s,%s,%s, %s, %s, %s, %s,%s,%s,%s,%s,%s, %s, %s, %s,%s,%s,%s,%s,%s, %s, %s , %s ,%s ,%s ,%s ,%s ,%s ,%s , %s, %s ,%s ,%s ,%s ,%s ,%s ,%s \n") % ( thres, count10, count11, count13, count131, count132, count133, count134, count135, count14, count1411, count1412, count145, count146, count12, count18, sumofgood, len(labellist) , inc10, inc11, inc13, inc131, inc132, inc133, inc134, inc135, inc14, inc1411, inc1412, inc145, inc146, inc12, inc18, inc, incorrect, totalfn , fncount10, fncount11, fncount13, fncount131, fncount132, fncount133, fncount134, fncount135, fncount14, fncount1411, fncount1412, fncount145, fncount146, fncount12, fncount18, normtp , normfp ))

#	f.write("Incorrect per class\n")
#	f.write(("%s,%s,%s,%s,%s,%s\n") % (inc1411, inc1412, inc145, inc146, inc18, inc12))
#	f.write("Incorrect label combinations = %s\n" % inc)
#	f.write("size good: %s\n"%len(labellist))
#	f.write( "Bad: %s\n"% bad)
#	f.write("size bad: %s\n"% len(bad))
#	f.write("When Threshold: %s, Incorrect: %s\n"%(thres,inc))
	f.close()
	history = []
	thres = thres - 0.05

