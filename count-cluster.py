import re
import csv

#history
#cache
count300 = 0
count10 = 0
count100 = 0
count600 = 0
count700 = 0
count900 = 0
count1000 = 0
inc = 0
no100 = 0
labels = list()
labellist = list()
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

	print labellist
	return len(labellist)

reader = csv.reader( open("/home/fimz/Dev/disk-2/datasets/66-dataset/1306809242-ncd-out.txt",'r'), delimiter = ' ')
for line in reader:
	cache = line[0]
	val = line[2]
	if float(val) < 0.55:
#		print line
#		first = line[0]
#		if re.match(r'%s[0-9][0-9]-*'%first,line[1]):
#		if re.match(r'[0-9]-*',line[1]):
#			count10 = count10 + 1				
#			no10 = 0
#			print "10:",line
#		else: no10 = 1
		if re.match(r'^1\d{2}-*',line[0]):
			if re.match(r'^1[0-9]{2}-*', line[1]):
				count100 = count100 + 1				
				print "100:",line
				no100 = 0
				size = lookuplist(str(line[0]))
			else: no100 = 1
		else: no100 = 1
		if re.match(r'3[0-9][0-9]-*',line[0]):
			if re.match(r'3[0-9][0-9]-*',line[1]):
				count300 = count300 + 1				
				print "300:",line
				no300 = 0
			else: no300 = 1
		else: no300 = 1
		if re.match(r'6[0-9][0-9]-*',line[0]):
			if re.match(r'6[0-9][0-9]-*',line[1]):
				count600 = count600 + 1				
				print "600:",line
				no600 = 0
			else: no600 = 1
		else: no600 = 1
		if re.match(r'7[0-9][0-9]-*',line[0]):
			if re.match(r'7[0-9][0-9]-*',line[1]):
				count700 = count700 + 1				
				print "700:",line
				no700 = 0
			else: no700 = 1
		else: no700 = 1
		if re.match(r'9[0-9][0-9]-*',line[0]):
			if re.match(r'9[0-9][0-9]-*',line[1]):
				count900 = count900 + 1				
				print "900:",line
				no900 = 0
			else: no900 = 1
		else: no900 = 1
		if re.match(r'8[0-9]{2}-*',line[0]):
			if re.match(r'8[0-9]{2}-*',line[1]):
				count1000 = count1000 + 1				
				print "1000:",line
				no1000 = 0
			else: no1000 = 1
		else: no1000 = 1
		if no1000 == 1 and no900 == 1 and no700 == 1 and no600 == 1 and no300 == 1 and no100 == 1:
			inc = inc + 1
			print line	


print "Correct Labels =\n 10 = %s,\n 100 = %s,\n 300 = %s\n,\n 600 = %s,\n 700 = %s,\n 900 = %s,\n 800 = %s\n" % (count10, count100, count300, count600, count700, count900, count1000)
print "Incorrect labels = %s" % inc
print "size:",size


