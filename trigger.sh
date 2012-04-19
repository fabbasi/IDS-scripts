#!/bin/sh
sigdir=/home/fimz/Dev/datasets/balanced-raw/imbalanced-100 
#datdir=/home/fimz/Dev/datasets/balanced-raw/imbalanced-100
datdir=/home/fimz/Dev/datasets/testset
outdir=/home/fimz/Dev/datasets/500-results/rev/novelty
echo "RUNNING GET SCORES"
## GET SCORES
python get_scores.py --sigdir $sigdir --datdir $datdir --iter 1 --outdir $outdir --model mymodel.txt
echo "RUNNING GET ROC"
## GET ROC
python get_roc.py 3 $outdir
echo "RUNNING GET NOVELTY"
## GET NOVELTY
python get_novelty.py $datdir $outdir

