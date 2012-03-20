import Orange

housing = Orange.data.Table("housing.tab")

knn = Orange.classification.knn.kNNLearner()

estimators = [Orange.evaluation.reliability.Mahalanobis(k=3),
              Orange.evaluation.reliability.LocalCrossValidation(k = 10)]

reliability = Orange.evaluation.reliability.Learner(knn, estimators = estimators)

restimator = reliability(housing)
instance = housing[0]

value, probability = restimator(instance, result_type=Orange.classification.Classifier.GetBoth)

for estimate in probability.reliability_estimate:
    print estimate.method_name, estimate.estimate
