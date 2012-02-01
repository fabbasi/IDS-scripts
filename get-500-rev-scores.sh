#!/bin/bash
## Trigger to calculate ncd, spamsum and their combined edit distances across all 10 datasets 
## Invokes rev-combncdspam python script
## Usage:
## python rev-combncdspam.py /path/to/dataset iteration /path/to/result
## python rev-combncdspam.py /home/fimz/Dev/datasets/500-dataset/$i $i /home/fimz/Dev/datasets/500-results
##
rm list500.txt
i='1'
#for i in `seq 1 3`
#do
	echo $i
	
#	python rev-combncdspam.py --sigdir /home/fimz/Dev/datasets/signatures/balanced --datdir /home/fimz/Dev/datasets/balanced-raw/imbalanced-20 --iter $i --outdir /home/fimz/Dev/datasets/500-results/rev/imbalanced-20 

#	python rev-combncdspam.py --sigdir /home/fimz/Dev/datasets/signatures/balanced --datdir /home/fimz/Dev/datasets/balanced-raw/imbalanced-50 --iter $i --outdir /home/fimz/Dev/datasets/500-results/rev/imbalanced-50 

#	python rev-combncdspam.py --sigdir /home/fimz/Dev/datasets/signatures/balanced --datdir /home/fimz/Dev/datasets/balanced-raw/imbalanced-100 --iter $i --outdir /home/fimz/Dev/datasets/500-results/rev/imbalanced-100 

	python rev-combncdspam.py --sigdir /home/fimz/Dev/datasets/balanced-raw/imbalanced-100  --datdir /home/fimz/Dev/datasets/balanced-raw/imbalanced-100 --iter $i --outdir /home/fimz/Dev/datasets/500-results/rev/imbalanced-100 
	

#	python rev-combncdspam.py --sigdir /home/fimz/Dev/datasets/signatures/balanced --datdir /home/fimz/Dev/datasets/balanced-raw/10-each --iter $i --outdir /home/fimz/Dev/datasets/500-results/rev/balanced 

#	python rev-combncdspam.py --sigdir /home/fimz/Dev/datasets/signatures/balanced --datdir /home/fimz/Dev/datasets/balanced-raw/10-each --iter $i --outdir /home/fimz/Dev/datasets/500-results/rev/balanced 

#	python rev-combncdspam.py --sigdir /home/fimz/Dev/datasets/signatures/balanced --datdir /home/fimz/Dev/datasets/balanced-raw/10-each --iter $i --outdir /home/fimz/Dev/datasets/500-results/rev/balanced 

	#	python rev-combncdspam.py --sigdir /home/fimz/Dev/datasets/500-dataset/raw/$i --datdir /home/fimz/Dev/datasets/profiles-raw/ --iter $i --outdir /home/fimz/Dev/datasets/500-results/rev 

#	mv /home/fimz/Dev/scripts/output/* /home/fimz/Dev/datasets/500-results/rev/balanced/
	mv /home/fimz/Dev/scripts/output/* /home/fimz/Dev/datasets/500-results/rev/imbalanced-100/

#done
./run500-rev-dynamic.sh
