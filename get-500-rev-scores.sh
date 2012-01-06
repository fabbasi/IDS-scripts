#!/bin/bash
## Trigger to calculate ncd, spamsum and their combined edit distances across all 10 datasets 
## Invokes rev-combncdspam python script
## Usage:
## python rev-combncdspam.py /path/to/dataset iteration /path/to/result
## python rev-combncdspam.py /home/fimz/Dev/datasets/500-dataset/$i $i /home/fimz/Dev/datasets/500-results
##
rm list500.txt
#i='1'
for i in `seq 1 3`
do
	echo $i
	python rev-combncdspam.py --sigdir /home/fimz/Dev/datasets/signatures/50 --datdir /home/fimz/Dev/datasets/500-dataset/raw/$i --iter $i --outdir /home/fimz/Dev/datasets/500-results/rev -g
	mv /home/fimz/Dev/scripts/output/* /home/fimz/Dev/datasets/500-results/rev/$i/
done
sh run500-rev-dynamic.sh
