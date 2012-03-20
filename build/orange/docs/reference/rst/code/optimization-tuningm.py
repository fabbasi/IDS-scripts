import Orange

learner = Orange.classification.tree.TreeLearner()
voting = Orange.data.Table("voting")
tuner = Orange.optimization.TuneMParameters(learner=learner,
             parameters=[("min_subset", [2, 5, 10, 20]),
                         ("measure", [Orange.feature.scoring.GainRatio(), 
                                      Orange.feature.scoring.Gini()])],
             evaluate = Orange.evaluation.scoring.AUC)

classifier = tuner(voting)
