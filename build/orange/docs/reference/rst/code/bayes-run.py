# Description: Naive Bayes Learner on iris data set
# Category:    classification
# Uses:        titanic
# Referenced:  Orange.classification.bayes
# Classes:     Orange.classification.bayes.NaiveLearner, Orange.classification.bayes.NaiveClassifier

import Orange
titanic = Orange.data.Table("titanic.tab")

learner = Orange.classification.bayes.NaiveLearner()
classifier = learner(titanic)

for inst in titanic[:5]:
    print inst.getclass(), classifier(inst)
