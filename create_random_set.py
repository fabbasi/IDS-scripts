###############
# Author: Fahim, 20111120
# Desc: Pick 500 binaries/files randomly from the target folder supplied as a parameter and write them out to a subset folder.
##################

import os
import sys
import random
import random
import shutil

folder = sys.argv[1]
listing = os.listdir(folder)

for d in range(1,6):
	d = "./" + str(d)
	if not os.path.exists(d):
		os.makedirs(d)
		dst = d + "/" 
		for i in range(500):
			random.shuffle(listing)		
			name =  str(random.choice(listing))
			src = "./" + folder + name
			shutil.copy(src,dst+name)
