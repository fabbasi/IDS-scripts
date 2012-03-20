import Orange

bridges = Orange.data.Table("bridges")
outlier_det = Orange.data.outliers.OutlierDetection()
outlier_det.set_examples(bridges, Orange.distance.Euclidean(bridges))
outlier_det.set_knn(3)
z_values = outlier_det.z_values()
for ex, zv in sorted(zip(bridges, z_values), key=lambda x: x[1])[-5:]:
    print ex, "Z-score: %5.3f" % zv
