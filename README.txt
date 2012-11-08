Steps involved in using our exemplar-learning system:

1. Create a model:
Use the get_model.py script:
python get_model.py training-set output-dir
python get_model.py /home/fimz/Dev/datasets/training/ /home/fimz/Dev/datasets/500-results/raw/

2. Find similarity scores between exemplars and test set
Use the get_scores.py script:
python get_scores.py -s /home/fimz/Dev/datasets/payload-tr -d /home/fimz/Dev/datasets/payload-test -o /home/fimz/Dev/datasets/500-results -m mymodel.txt
