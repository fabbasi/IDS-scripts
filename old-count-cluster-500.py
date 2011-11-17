import re
import csv

#history
#cache
count13 = 0
count10 = 0
count11 = 0
count12 = 0
count14 = 0
count15 = 0
count16 = 0
count17 = 0
count18 = 0
inc = 0
no100 = 0
labels = list()
labellist = list()
badlist = list()
result = list()
#thres = sys.argv[1]

def lookupbad(value):
        a = value[0]
        b = value[1]
        s = value[2]
        label = a+","+b+","+s
        if not badlist:
                badlist.append(label)
        for labels in badlist:
                if label in badlist:
                        1
                else:
                        badlist.append(label)

#       print labellist
        return badlist

#reader = csv.reader( open("1305675944-ncd-out.txt",'r'), delimiter = ' ')
#for line in reader:
#	history = line[0]
#	break

def lookuplist(label):
	if not labellist:
		labellist.append(label)
	for labels in labellist:
		if label in labellist:
			1
		else:
			labellist.append(label)

#	print labellist
	return labellist


thres = 0.5

while thres < 0.9:
	reader = csv.reader( open("/home/fimz/Dev/datasets/500-dataset/1305157228-ncd-out.txt",'r'), delimiter = ' ')
	for line in reader:
	#	cache = line[0]
		val = line[2]
		if float(val) < float(thres):
			if re.match(r'^10-*',line[0]):
				if re.match(r'^10-*', line[1]):
					count10 = count10 + 1				
		#			print "10:",line
					no10 = 0
					lookuplist(str(line[0]))
				else: no10 = 1
			else: no10 = 1
			if re.match(r'11-*',line[0]):
				if re.match(r'11-*',line[1]):
					count11 = count11 + 1				
#					print "11:",line
					lookuplist(str(line[0]))
					no11 = 0
				else: no11 = 1
			else: no11 = 1
			if re.match(r'12-*',line[0]):
				if re.match(r'12-*',line[1]):
					count12 = count12 + 1				
#					print "12:",line
					no12 = 0
					lookuplist(str(line[0]))
				else: no12 = 1
			else: no12 = 1
			if re.match(r'13*-*',line[0]):
				if re.match(r'13*-*',line[1]):
					count13 = count13 + 1				
#					print "13:",line
					no13 = 0
					lookuplist(str(line[0]))
				else: no13 = 1
			else: no13 = 1
			if re.match(r'14*-*',line[0]):
				if re.match(r'14*-*',line[1]):
					count14 = count14 + 1				
#					print "14:",line
					no14 = 0
					lookuplist(str(line[0]))
				else: no14 = 1
			else: no14 = 1
			if re.match(r'15-*',line[0]):
				if re.match(r'15-*',line[1]):
					count15 = count15 + 1				
#					print "15:",line
					no15 = 0
					lookuplist(str(line[0]))
				else: no15 = 1
			else: no15 = 1
			if re.match(r'16-*',line[0]):
				if re.match(r'16-*',line[1]):
					count16 = count16 + 1				
#					print "16:",line
					no16 = 0
					lookuplist(str(line[0]))
				else: no16 = 1
			else: no16 = 1
			if re.match(r'17-*',line[0]):
				if re.match(r'17-*',line[1]):
					count17 = count17 + 1				
#					print "17:",line
					no17 = 0
					lookuplist(str(line[0]))
				else: no17 = 1
			else: no17 = 1
			if re.match(r'18-*',line[0]):
				if re.match(r'18-*',line[1]):
					count18 = count18 + 1				
#					print "18:",line
					no18 = 0
					lookuplist(str(line[0]))
				else: no18 = 1
			else: no18 = 1

			if no10 == 1 and no11 == 1 and no12 == 1 and no13 == 1 and no14 == 1 and no15 == 1 and no16 == 1 and no17 == 1 and no18 == 1  :
				inc = inc + 1
				lookupbad(line)
				print line	

	labellist = lookuplist(line[0])
	print "Correct Labels =\n 10 = %s,\n 11 = %s,\n 12 = %s\n,\n 13 = %s,\n 14 = %s,\n 15 = %s,\n 16 = %s\n 17 = %s\n 18 = %s\n" % (count10, count11, count12, count13, count14, count15, count16, count17, count18)
	print "Incorrect labels = %s" % inc
	print labellist
	print "size Good:",len(labellist)
	bad = lookupbad(line)
	print "Bad:\n", bad
	print "size bad:", len(bad)
	print "When Threshold: %s, Incorrect: %s"%(thres,inc)

	result.append( str(count10) + " , " + str(count11) + " , " +str( count12) +" , " + str(count13) + " , " + str(count14) + " , " + str(count15) + " , " + str(count16) +" , " + str(count17) +" , " +  str(count18) + "," + "Size Good: %s"%len(labellist) + " , " +  "Size Bad: %s"%(len(bad) ))

	thres = thres + 0.1

print result
