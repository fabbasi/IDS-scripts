#!/bin/sh
#sigdir=/home/fimz/Dev/datasets/balanced-raw/imbalanced-100 
#sigdir=/home/fimz/Dev/datasets/balanced-raw/imbalanced-500 
#sigdir=/home/fimz/Dev/malware-collection/407-labelled 
sigdir=/home/fimz/Dev/malware-collection/500-train 

#datdir=/home/fimz/Dev/datasets/balanced-raw/imbalanced-500
#datdir=/home/fimz/Dev/datasets/testset
#datdir=/home/fimz/Dev/datasets/dionaea-streams
#datdir=/home/fimz/Dev/datasets/dionaea-testset-1
datdir=/home/fimz/Dev/malware-collection/6000-labelled

#outdir=/home/fimz/Dev/datasets/500-results/rev/novelty
#outdir=/home/fimz/Dev/datasets/500-results/rev/dionaea
outdir=/home/fimz/Dev/datasets/500-results/rev/malware

echo "RUNNING GET MODEL, to create a model from our training dataset"
#python get_model.py $sigdir $outdir
echo "Move results to result folder..."
#mv matrx.csv $outdir
#mv *.png $outdir
echo "RUNNING GET SCORES, to create distance matrix of similarity scores between the test set and the training set"
## GET SCORES
#python get_scores.py --sigdir $sigdir --datdir $datdir --iter 1 --outdir $outdir --model mymodel.txt
echo "RUNNING GET ROC, to create a confusion matrix and ROC curve for the classifier"
## GET ROC
python get_roc.py 3 $outdir
echo "RUNNING GET NOVELTY, to detect unknown/unseen samples and suggest model for them"
## GET NOVELTY
#python get_novelty.py $datdir $sigdir $outdir
