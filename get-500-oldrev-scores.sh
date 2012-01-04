#!/bin/bash
## Trigger to calculate ncd, spamsum and their combined edit distances across all 10 datasets 
## Invokes rev-combncdspam python script
## Usage:
## python rev-combncdspam.py /path/to/dataset iteration /path/to/result
## python rev-combncdspam.py /home/fimz/Dev/datasets/500-dataset/$i $i /home/fimz/Dev/datasets/500-results
##
rm list500.txt
#for i in `seq 1 3`
i='1'
#do
	echo $i
#	python reverse-oldscore.py /home/fimz/Dev/datasets/500-dataset/rev/$i $i /home/fimz/Dev/datasets/500-results/rev
	python reverse-oldscore.py /home/fimz/Dev/scripts/profiles-rev/$i $i /home/fimz/Dev/scripts/profiles-rev
	mv /home/fimz/Dev/scripts/output/* /home/fimz/Dev/datasets/500-results/rev/$i/
#done
sh run500-rev-dynamic.sh
